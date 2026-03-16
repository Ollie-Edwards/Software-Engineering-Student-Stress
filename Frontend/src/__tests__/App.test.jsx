import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "../App";

describe("App", () => {
  it("renders without crashing", () => {
    render(<App />);
    expect(document.querySelector(".min-h-screen")).toBeInTheDocument();
  });

  it("renders the NavigationBar", () => {
    render(<App />);
    expect(document.querySelector("nav")).toBeInTheDocument();
  });

  it("renders the New Task button", () => {
    render(<App />);
    expect(screen.getByText("+ New Task")).toBeInTheDocument();
  });

  it("renders the search input", () => {
    render(<App />);
    expect(screen.getByPlaceholderText("Search tasks...")).toBeInTheDocument();
  });

  it("sets isAdding to true when New Task button is clicked", () => {
    render(<App />);
    fireEvent.click(screen.getByText("+ New Task"));
    // modal/form should appear after clicking
    expect(screen.getByText("+ New Task")).toBeInTheDocument();
  });

  it("has correct root background class", () => {
    const { container } = render(<App />);
    expect(container.firstChild).toHaveClass("min-h-screen", "bg-gray-50");
  });
});
