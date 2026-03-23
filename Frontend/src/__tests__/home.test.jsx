import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import Home from "../pages/Home";

const mockTasks = [
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
      expect(titles[0]).toHaveTextContent('Finish ML coursework')
      expect(titles[1]).toHaveTextContent('Software Engineering presentation')
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

    it("removes the task from the list after deletion", async () => {})
    it("does not delete if confirm is cancelled", async () => {})
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

})