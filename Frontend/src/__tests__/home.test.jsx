import React from "react";

import { MemoryRouter } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect } from "vitest";
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
  }
]

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn((url) => {
    if (url === 'http://localhost:8000/tasks') {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockTasks),
      })
    }
    return Promise.resolve({ ok: true, json: () => Promise.resolve({}) })
  }))
})

describe("Home", () => {

  describe("Rendering", () => {
    it("renders without crashing", async () => {
      renderHome()
      await screen.findByText('Tasks')
      expect(screen.getByText('Tasks')).toBeInTheDocument()
      expect(screen.getByText(/tasks remaining/i)).toBeInTheDocument()
      expect(screen.getByText(/sort by/i)).toBeInTheDocument()
      expect(screen.getByText(mockTasks[0].title)).toBeInTheDocument()
    })

    it("shows no tasks found when list is empty", async () => {
      fetch.mockImplementationOnce(() =>
        Promise.resolve({ ok: true, json: () => Promise.resolve([]) })
      )
      renderHome()
      expect(await screen.findByText('No tasks found.')).toBeInTheDocument()
    })

    it("shows error state when fetch fails", async () => {
      fetch.mockImplementationOnce(() =>
        Promise.resolve({ ok: false })
      )
      renderHome()
      expect(await screen.findByText(/HTTP error/i)).toBeInTheDocument()
    })
  })

  describe("Sorting", () => {
    it("sorts highest to lowest by default", async () => {})
    it("sorts lowest to highest when dropdown changed", async () => {})
  })

  describe("Complete task", () => {
    it("calls the complete endpoint when button clicked", async () => {
      const user = userEvent.setup()
      renderHome()
      await screen.findByText('Tasks')

      await user.click(screen.getAllByTitle('Toggle Complete Task')[0])

      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8000/tasks/task/2/complete',
        { method: 'POST' }
      )
    })

    it("calls the reopen endpoint when clicking a completed task", async () => {})
  })

  describe("Delete task", () => {
    it("calls the delete endpoint after confirming", async () => {})
    it("removes the task from the list after deletion", async () => {})
    it("does not delete if confirm is cancelled", async () => {})
  })

  describe("Edit modal", () => {
    it("opens when a task card is clicked", async () => {})
    it("is pre-filled with the task title", async () => {})
    it("closes when cancel is clicked", async () => {})
    it("calls the PUT endpoint on submit", async () => {})
  })

  describe("Create modal", () => {
    it("shows when isAdding is true", async () => {})
    it("calls setIsAdding(false) when × is clicked", async () => {})
  })

})