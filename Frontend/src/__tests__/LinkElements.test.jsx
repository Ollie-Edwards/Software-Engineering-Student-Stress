import React from "react";

import { MemoryRouter } from "react-router-dom";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect } from "vitest";
import LinkElement from "../components/LinkElement";

describe("linkElement", () => {
  it('when url is provided button is rendered', async () => {
    render(<LinkElement url="https://example.com"/>)
    expect(screen.getByRole("button")).toBeInTheDocument()
  })

  it('when url is not provided button is not rendered', async () => {
    render(<LinkElement url={null}/>)
    expect(screen.queryByRole("button")).not.toBeInTheDocument()
  })

  it('When button is clicked, the link opens in new tab', async () => {
    const user = userEvent.setup()
    window.open = vi.fn()

    render(<LinkElement url="https://example.com"/>)
    // Expect button to be rendered first
    const linkButton = screen.getByRole("button")
    expect(linkButton).toBeInTheDocument()
    await user.click(linkButton)

    // Then when the button is clicked, expect the webpage to open
    expect(window.open).toHaveBeenCalledWith("https://example.com", "_blank")
  })
});