import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Home from "../pages/Home";
import { describe } from "vitest";

const mockTasks = [
  // medium priority
  {
    id: 1,
    title: "Finish ML coursework",
    description: "Jupyter Notebook",
    importance: 4,
    length: 60,
    due_at: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    completed: false,
    reminder: false,
    reference_url: null,
    subtasks: [],
  },
  // high priority
  {
    id: 2,
    title: "Software Engineering presentation",
    description: "Book room",
    importance: 10,
    length: 30,
    due_at: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    completed: false,
    reminder: false,
    reference_url: null,
    subtasks: [],
  },
  // low priority
  {
    id: 3,
    title: "Buy New Sofa",
    description: "Purchase online",
    importance: 1,
    length: 5,
    due_at: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    completed: false,
    reminder: false,
    reference_url: null,
    subtasks: [],
  },
]

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn((url) => {
    if (url === 'http://localhost:8000/tasks') {
      return Promise.resolve({ ok: true, json: () => Promise.resolve(mockTasks) })
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
  }))

  vi.stubGlobal('confirm', vi.fn(() => true))
})

afterEach(() => {
  vi.restoreAllMocks()
})

const renderHome = async () => {
  render(<Home isAdding={false} setIsAdding={vi.fn()} />)
  await screen.findByText('Tasks')
}

describe("Home", () => {

  describe("Rendering", () => {
    it("renders without crashing", async () => {
      await renderHome()
      expect(screen.getByText('Tasks')).toBeInTheDocument()
      expect(screen.getByText(/tasks remaining/i)).toBeInTheDocument()
      expect(screen.getByText(/sort by/i)).toBeInTheDocument()
      expect(screen.getByText(mockTasks[0].title)).toBeInTheDocument()
    })

    it("shows no tasks found when list is empty", async () => {
      fetch.mockImplementationOnce(() =>
        Promise.resolve({ ok: true, json: () => Promise.resolve([]) })
      )
      render(<Home isAdding={false} setIsAdding={vi.fn()} />)
      expect(await screen.findByText('No tasks found.')).toBeInTheDocument()
    })

    it("shows error state when fetch fails", async () => {
      fetch.mockImplementationOnce(() =>
        Promise.resolve({ ok: false })
      )
      render(<Home isAdding={false} setIsAdding={vi.fn()} />)
      expect(await screen.findByText(/HTTP error/i)).toBeInTheDocument()
    })
  })

  describe("Sorting", () => {
    it("sorts highest to lowest by default", async () => {
      await renderHome()

      const titles = screen.getAllByRole('heading', { level: 2 })
      expect(titles[0]).toHaveTextContent('Software Engineering presentation')
      expect(titles[1]).toHaveTextContent('Finish ML coursework')
    })

    it("sorts lowest to highest when dropdown changed", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.selectOptions(screen.getByRole('combobox'), 'asc')

      const titles = screen.getAllByRole('heading', { level: 2 })
      expect(titles[0]).toHaveTextContent('Buy New Sofa')
      expect(titles[1]).toHaveTextContent('Finish ML coursework')
      expect(titles[2]).toHaveTextContent('Software Engineering presentation')
    })
  })

  describe("Complete task", () => {
    it("calls the complete endpoint when button clicked", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getAllByTitle('Toggle Complete Task')[0])

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/tasks/task/2/complete',
        { method: 'POST' }
      )
    })

    it("calls the reopen endpoint when clicking a completed task", async () => {
      const completedTasks = [{ ...mockTasks[0], completed: true }]
      
      fetch.mockImplementationOnce(() =>
        Promise.resolve({ ok: true, json: () => Promise.resolve(completedTasks) })
      )

      const user = userEvent.setup()
      render(<Home isAdding={false} setIsAdding={vi.fn()} />)
      await screen.findByText('Finish ML coursework')

      await user.click(screen.getAllByTitle('Toggle Complete Task')[0])

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/tasks/task/1/reopen',
        { method: 'POST' }
      )
    })
  })

  describe("Create Task", () => {
    it("creates a new task", async () => {
      const user = userEvent.setup()
      render(<Home isAdding={true} setIsAdding={vi.fn()} />)
      await screen.findByText('Create New Task')

      await user.type(screen.getByPlaceholderText('Title'), 'New Test Task')
      await user.type(screen.getByPlaceholderText('Add some details...'), 'Some description')
      await user.type(screen.getByPlaceholderText('5'), '8')
      await user.type(screen.getByPlaceholderText('30'), '60')

      await user.click(screen.getByText('Create Task'))

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/tasks',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('New Test Task')
        })
      )
    })

    it("handles update task network error gracefully", async () => {
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(mockTasks) })
        }
        return Promise.reject(new Error('Network error'))
      })

      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByText('Software Engineering presentation'))
      await screen.findByText('Edit Task')
      await user.click(screen.getByText('Save Changes'))

      expect(screen.getByText('Tasks')).toBeInTheDocument()
    })

    it("reverts task completion if fetch returns ok: false", async () => {
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(mockTasks) })
        }
        return Promise.resolve({ ok: false })
      })

      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getAllByTitle('Toggle Complete Task')[0])

      expect(screen.getAllByText('Not Completed').length).toBeGreaterThan(0)
    })
  })

  describe("Delete task", () => {
    it("calls the delete endpoint after confirming", async () => {
      vi.stubGlobal('confirm', vi.fn(() => true))

      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getAllByTitle('Delete Task')[0])

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/tasks/2',
        { method: 'DELETE' }
      )
    })

    it("does not delete if confirm is cancelled", async () => {
      confirm.mockReturnValueOnce(false)
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getAllByTitle('Delete Task')[0])

      expect(fetch).not.toHaveBeenCalledWith(
        expect.stringContaining('/tasks/'),
        { method: 'DELETE' }
      )
    })

    it("calls the PUT endpoint when edit form is submitted", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByText('Software Engineering presentation'))
      await screen.findByText('Edit Task')
      await user.click(screen.getByText('Save Changes'))

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/tasks/2',
        expect.objectContaining({ method: 'PUT' })
      )
    })
  })

  describe("Edit modal", () => {
    it("opens when a task card is clicked", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByText('Software Engineering presentation'))

      expect(await screen.findByText('Edit Task')).toBeInTheDocument()
    })

    it("is pre-filled with the task title", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByText('Software Engineering presentation'))

      expect(await screen.findByDisplayValue('Software Engineering presentation')).toBeInTheDocument()
    })

    it("closes when cancel is clicked", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByText('Software Engineering presentation'))
      await screen.findByText('Edit Task')
      await user.click(screen.getByText('Cancel'))

      expect(screen.queryByText('Edit Task')).not.toBeInTheDocument()
    })

    it("calls the PUT endpoint on submit", async () => {})
  })

  describe("Create modal", () => {
    it("shows when isAdding is true", async () => {
      render(<Home isAdding={true} setIsAdding={vi.fn()} />)
      await screen.findByText('Create New Task')
      expect(screen.getByText('Create New Task')).toBeInTheDocument()
    })

    it("calls setIsAdding(false) when × is clicked", async () => {
      const setIsAdding = vi.fn()
      render(<Home isAdding={true} setIsAdding={setIsAdding} />)
      await screen.findByText('Create New Task')

      await userEvent.click(screen.getByTitle('Close Modal'))

      expect(setIsAdding).toHaveBeenCalledWith(false)
    })
  })

  describe("Subtasks", () => {
    const taskWithSubtasks = [{
      ...mockTasks[0],
      subtasks: [{
        id: 10,
        title: 'Write tests',
        completed: false,
      }]
    }]

    beforeEach(() => {
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(taskWithSubtasks) })
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
      })
    })

    it("shows subtasks when chevron is clicked", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getAllByTitle('Toggle Complete Task')[0].nextSibling.nextSibling)
      
      expect(await screen.findByText('Write tests')).toBeInTheDocument()
    })

    it("toggles a subtask checkbox", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getAllByTitle('Toggle Complete Task')[0].nextSibling.nextSibling)
      await screen.findByText('Write tests')

      await user.click(screen.getByRole('checkbox'))

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/tasks/subtask/10/complete',
        { method: 'POST' }
      )
    })

    it("deletes a subtask", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getAllByTitle('Toggle Complete Task')[0].nextSibling.nextSibling)
      await screen.findByText('Write tests')

      const deleteButtons = screen.getAllByTitle('Delete Subtask')
      await user.click(deleteButtons[deleteButtons.length - 1])

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/tasks/subtasks/10',
        expect.objectContaining({ method: 'DELETE' })
      )
    })

    it("adds a subtask", async () => {
      const user = userEvent.setup()
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(taskWithSubtasks) })
        }
        if (url === 'http://localhost:8000/tasks/subtasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve({ id: 11, title: 'New subtask', completed: false }) })
        }
        return Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
      })

      await renderHome()

      await user.click(screen.getAllByTitle('Toggle Complete Task')[0].nextSibling.nextSibling)
      await screen.findByText('Add Subtask')

      await user.click(screen.getByText('Add Subtask'))
      await user.type(screen.getByPlaceholderText('What needs to be done?'), 'New subtask')
      await user.click(screen.getByText('Add'))

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/tasks/subtasks',
        expect.objectContaining({ method: 'POST' })
      )
    })

    it("edit a subtask", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getAllByTitle('Toggle Subtasks')[0])
      await screen.findByText('Write tests')

      await user.click(screen.getByText('Write tests'))

      const input = screen.getByDisplayValue('Write tests')
      await user.clear(input)
      await user.type(input, 'Updated subtask')

      await user.keyboard('{Enter}')

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/tasks/subtasks/10',
        expect.objectContaining({ method: 'PUT' })
      )
    })

    it("pressing Escape cancels subtask editing", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByTitle('Toggle Subtasks'))
      await screen.findByText('Write tests')

      await user.click(screen.getByText('Write tests'))
      expect(screen.getByDisplayValue('Write tests')).toBeInTheDocument()

      await user.keyboard('{Escape}')

      expect(screen.queryByDisplayValue('Write tests')).not.toBeInTheDocument()
      expect(screen.getByText('Write tests')).toBeInTheDocument()
    })

    it("handles subtask delete returning false", async () => {
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(taskWithSubtasks) })
        }
        return Promise.resolve({ ok: false })
      })

      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByTitle('Toggle Subtasks'))
      await screen.findByText('Write tests')
      await user.click(screen.getByTitle('Delete Subtask'))

      expect(screen.getByText('Write tests')).toBeInTheDocument()
    })

    it("handles subtask delete network error gracefully", async () => {
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(taskWithSubtasks) })
        }
        return Promise.reject(new Error('Network error'))
      })

      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByTitle('Toggle Subtasks'))
      await screen.findByText('Write tests')
      await user.click(screen.getByTitle('Delete Subtask'))

      expect(screen.getByText('Tasks')).toBeInTheDocument()
    })

    it("handles subtask toggle network error gracefully", async () => {
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(taskWithSubtasks) })
        }
        return Promise.reject(new Error('Network error'))
      })

      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByTitle('Toggle Subtasks'))
      await screen.findByText('Write tests')

      await user.click(screen.getByRole('checkbox'))

      expect(screen.getByText('Tasks')).toBeInTheDocument()
    })

    it("handles add subtask network error gracefully", async () => {
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(taskWithSubtasks) })
        }
        return Promise.reject(new Error('Network error'))
      })

      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByTitle('Toggle Subtasks'))
      await screen.findByText('Add Subtask')

      await user.click(screen.getByText('Add Subtask'))
      await user.type(screen.getByPlaceholderText('What needs to be done?'), 'New subtask')
      await user.click(screen.getByText('Add'))

      expect(screen.getByText('Tasks')).toBeInTheDocument()
    })

    it("handles update subtask network error gracefully", async () => {
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(taskWithSubtasks) })
        }
        return Promise.reject(new Error('Network error'))
      })

      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByTitle('Toggle Subtasks'))
      await screen.findByText('Write tests')

      await user.click(screen.getByText('Write tests'))
      const input = screen.getByDisplayValue('Write tests')
      await user.clear(input)
      await user.type(input, 'Updated subtask')
      await user.keyboard('{Enter}')

      expect(screen.getByText('Tasks')).toBeInTheDocument()
    })
  })

  describe("Error handlers", () => {
    it("handles complete fetch failure gracefully", async () => {
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(mockTasks) })
        }
        return Promise.reject(new Error('Network error'))
      })

      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getAllByTitle('Toggle Complete Task')[0])

      expect(screen.getByText('Tasks')).toBeInTheDocument()
    })

    it("handles delete fetch failure gracefully", async () => {
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(mockTasks) })
        }
        return Promise.reject(new Error('Network error'))
      })

      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getAllByTitle('Delete Task')[0])

      expect(screen.getByText('Tasks')).toBeInTheDocument()
    })

    it("handles delete returning ok: false gracefully", async () => {
      fetch.mockImplementation((url) => {
        if (url === 'http://localhost:8000/tasks') {
          return Promise.resolve({ ok: true, json: () => Promise.resolve(mockTasks) })
        }
        return Promise.resolve({ ok: false })
      })

      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getAllByTitle('Delete Task')[0])

      expect(screen.getByText('Tasks')).toBeInTheDocument()
      expect(screen.getByText('Software Engineering presentation')).toBeInTheDocument()
    })

    it("closes edit modal when the task being edited is deleted", async () => {
      const user = userEvent.setup()
      await renderHome()

      await user.click(screen.getByText('Software Engineering presentation'))
      await screen.findByText('Edit Task')

      await user.click(screen.getAllByTitle('Delete Task')[0])

      expect(screen.queryByText('Edit Task')).not.toBeInTheDocument()
    })
  })
})