import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import MaintenanceBanner from "../components/maintenance-banner";

describe("MaintenanceBanner", () => {
  it("renders the maintenance message", () => {
    render(<MaintenanceBanner />);
    expect(screen.getByText(/System Update/i)).toBeInTheDocument();
  });
});
