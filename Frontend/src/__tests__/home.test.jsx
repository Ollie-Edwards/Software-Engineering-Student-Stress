import React from "react";

import { MemoryRouter } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect } from "vitest";
import Home from "../pages/Home";

const mockTasks = [
  {
    id: 1,
    title: "Finish homework",
    description: "Math and English",
    importance: 8,
    length: 60,
    due_at: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    completed: false,
    reminder: false,
    reference_url: null,
    subtasks: [],
  }
]

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve(mockTasks),
    })
  ))
})

describe("Home", () => {
  it("base task page renders without crashing", async () => {
    render(<Home isAdding={false} setIsAdding={vi.fn()} />);
    await screen.findByText('Tasks')

    expect(screen.getByText('Tasks')).toBeInTheDocument();

    expect(screen.getByText(/tasks remaining/i)).toBeInTheDocument()
    expect(screen.getByText(/sort by/i)).toBeInTheDocument()
    expect(screen.getByText('Finish homework')).toBeInTheDocument()
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
    expect(await screen.findByText('HTTP error')).toBeInTheDocument()
  });
}) 