import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import HeaderSection from "../components/header-section";

beforeEach(() => {
  Object.defineProperty(window, "IntersectionObserver", {
    value: jest.fn().mockImplementation(() => ({
      observe: jest.fn(),
      disconnect: jest.fn(),
      unobserve: jest.fn(),
      takeRecords: jest.fn().mockReturnValue([]),
      root: null,
      rootMargin: "",
      thresholds: [],
    })),
    writable: true,
  });
});

describe("HeaderSection", () => {
  it("renders the OmniBrief brand link", () => {
    render(<HeaderSection />);
    expect(screen.getByText("OmniBrief")).toBeInTheDocument();
  });

  it("renders navigation links", () => {
    render(<HeaderSection />);
    expect(screen.getByText("Why")).toBeInTheDocument();
    expect(screen.getByText("How it works")).toBeInTheDocument();
    expect(screen.getByText(/Who it's for/)).toBeInTheDocument();
  });

  it("renders the GitHub link", () => {
    render(<HeaderSection />);
    expect(screen.getByLabelText(/View OmniBrief on GitHub/i)).toBeInTheDocument();
  });
});
