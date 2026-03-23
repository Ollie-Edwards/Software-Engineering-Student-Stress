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
  it("base task page renders without crashing", async () => {
    render(<Home isAdding={false} setIsAdding={vi.fn()} />);
    await screen.findByText('Tasks')

    expect(screen.getByText('Tasks')).toBeInTheDocument();

    expect(screen.getByText(/tasks remaining/i)).toBeInTheDocument()
    expect(screen.getByText(/sort by/i)).toBeInTheDocument()
    expect(screen.getByText(mockTasks[0]["title"])).toBeInTheDocument()
  });

  it("task page handles no tasks being returned", async () => {
    // Override "beforeEach" fetch
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([]),
      })
    )

    render(<Home isAdding={false} setIsAdding={vi.fn()} />)
    expect(await screen.findByText('No tasks found.')).toBeInTheDocument()
  });

  it("task page handles error if fetch fails", async () => {
    // Override "beforeEach" fetch to fail
    fetch.mockImplementationOnce(() =>
      Promise.resolve({ ok: false })
    )

    render(<Home isAdding={false} setIsAdding={vi.fn()} />)
    expect(await screen.findByText(/HTTP error/i)).toBeInTheDocument()
  });

  it("Completing a task sends correct POST request", async () => {
    const user = userEvent.setup()
    render(<Home isAdding={false} setIsAdding={vi.fn()} />)
    await screen.findByText('Tasks')

    await user.click(screen.getAllByTitle('Toggle Complete Task')[0])

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/tasks/task/2/complete',
      { method: 'POST' }
    )
  });
}) 