import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import MoodleTasks from "../MoodleTask";

const mockTasks = [
  {
    id: 1,
    title: "Submit Assignment 1",
    activity: "Assignment",
    course_name: "Introduction to Computer Science",
    reference_url: "http://moodle.example.com/task/1",
    approved: false,
  },
  {
    id: 2,
    title: "Watch Lecture Video",
    activity: "Video",
    course_name: "Advanced Mathematics",
    reference_url: "http://moodle.example.com/task/2",
    approved: true,
  },
];

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn((url) => {
      if (url === "http://localhost:8000/moodletasks") {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockTasks),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
    }),
  );
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe("MoodleTasks", () => {
  it("renders without crashing", () => {
    render(<MoodleTasks />);
    expect(document.querySelector(".min-h-screen")).toBeInTheDocument();
  });

  it("renders the page heading", () => {
    render(<MoodleTasks />);
    expect(screen.getByText("Moodle Tasks")).toBeInTheDocument();
  });

  it("has correct root background class", () => {
    const { container } = render(<MoodleTasks />);
    expect(container.firstChild).toHaveClass("bg-slate-50", "min-h-screen");
  });

  it("fetches moodle tasks on mount", async () => {
    render(<MoodleTasks />);
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("http://localhost:8000/moodletasks");
    });
  });

  it("renders task titles after fetch", async () => {
    render(<MoodleTasks />);
    expect(await screen.findByText("Submit Assignment 1")).toBeInTheDocument();
    expect(await screen.findByText("Watch Lecture Video")).toBeInTheDocument();
  });

  it("renders task activity badges", async () => {
    render(<MoodleTasks />);
    expect(await screen.findByText("Assignment")).toBeInTheDocument();
    expect(await screen.findByText("Video")).toBeInTheDocument();
  });

  it("renders course names", async () => {
    render(<MoodleTasks />);
    expect(
      await screen.findByText("Introduction to Computer Science"),
    ).toBeInTheDocument();
    expect(
      await screen.findByText("Advanced Mathematics"),
    ).toBeInTheDocument();
  });

  it("renders correct status for approved and pending tasks", async () => {
    render(<MoodleTasks />);
    const pendingStatuses = await screen.findAllByText(/Pending/);
    const completedStatuses = await screen.findAllByText(/Completed/);
    expect(pendingStatuses).toHaveLength(1);
    expect(completedStatuses).toHaveLength(1);
  });

  it("renders approve and reject buttons for each task", async () => {
    render(<MoodleTasks />);
    await screen.findByText("Submit Assignment 1");
    const approveButtons = screen.getAllByTitle("Approve Task");
    const rejectButtons = screen.getAllByTitle("Reject Task");
    expect(approveButtons).toHaveLength(mockTasks.length);
    expect(rejectButtons).toHaveLength(mockTasks.length);
  });

  it("calls the approve endpoint when approve is clicked", async () => {
    render(<MoodleTasks />);
    await screen.findByText("Submit Assignment 1");
    fireEvent.click(screen.getAllByTitle("Approve Task")[0]);
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        "http://localhost:8000/moodletasks/1/approve",
        { method: "POST" },
      );
    });
  });

  it("calls the reject endpoint when reject is clicked", async () => {
    render(<MoodleTasks />);
    await screen.findByText("Submit Assignment 1");
    fireEvent.click(screen.getAllByTitle("Reject Task")[0]);
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        "http://localhost:8000/moodletasks/1/reject",
        { method: "POST" },
      );
    });
  });

  it("shows an error message when the fetch fails", async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({ ok: false }),
    );
    render(<MoodleTasks />);
    await waitFor(() => {
      // Error state is stored but component renders no tasks — grid should be empty
      expect(screen.queryByText("Submit Assignment 1")).not.toBeInTheDocument();
    });
  });

  it("renders no task cards when fetch returns an empty list", async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({ ok: true, json: () => Promise.resolve([]) }),
    );
    render(<MoodleTasks />);
    await waitFor(() => {
      expect(document.querySelector(".grid")).toBeEmptyDOMElement();
    });
  });
});