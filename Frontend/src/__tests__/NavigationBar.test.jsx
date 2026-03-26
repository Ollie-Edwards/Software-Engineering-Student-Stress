import React from "react";

import { MemoryRouter } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect } from "vitest";
import NavigationBar from "../components/NavigationBar";

describe("NavigationBar", () => {
  it('handles back to main', async () => {
    const user = userEvent.setup()
    
    render(
      <MemoryRouter initialEntries={["/moodle"]}>
        <NavigationBar />
      </MemoryRouter>
    )

    // get all approval buttons on page - click the top one
    const backButton = await screen.getByText(/Back to Main/i)
    await user.click(backButton)

    expect(window.location.pathname).toBe('/')
  })
});