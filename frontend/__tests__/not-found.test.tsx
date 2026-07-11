import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import NotFound from "../app/not-found";

describe("NotFound", () => {
  it("renders 404 heading", () => {
    render(<NotFound />);
    expect(screen.getByText("404")).toBeInTheDocument();
  });

  it("renders a link to the home page", () => {
    render(<NotFound />);
    expect(screen.getByText("Go home")).toBeInTheDocument();
  });
});
