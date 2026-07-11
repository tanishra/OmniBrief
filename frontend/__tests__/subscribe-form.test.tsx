import "@testing-library/jest-dom";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SubscribeForm from "../components/subscribe-form";

jest.mock("../lib/api", () => ({
  post: jest.fn(),
}));

const mockPost = jest.mocked(require("../lib/api").post);

describe("SubscribeForm", () => {
  beforeEach(() => {
    mockPost.mockReset();
  });

  it("renders the subscribe form", () => {
    render(<SubscribeForm />);
    expect(screen.getByText(/Subscribe in under 10 seconds/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Enter your work email/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Subscribe/i })).toBeInTheDocument();
  });

  it("shows success message on submission", async () => {
    mockPost.mockResolvedValue({ message: "Check your email to confirm." });
    const user = userEvent.setup();

    render(<SubscribeForm />);
    await user.type(screen.getByPlaceholderText(/Enter your work email/i), "test@test.com");
    await user.click(screen.getByRole("button", { name: /Subscribe/i }));

    expect(await screen.findByText(/Check your inbox/i)).toBeInTheDocument();
  });

  it("shows error message on failure", async () => {
    mockPost.mockRejectedValue(new Error("Network error"));
    const user = userEvent.setup();

    render(<SubscribeForm />);
    await user.type(screen.getByPlaceholderText(/Enter your work email/i), "test@test.com");
    await user.click(screen.getByRole("button", { name: /Subscribe/i }));

    expect(await screen.findByText(/Something went wrong/i)).toBeInTheDocument();
  });

  it("shows the compact variant with max-w-md", () => {
    const { container } = render(<SubscribeForm compact />);
    expect(container.querySelector(".max-w-md")).toBeInTheDocument();
  });
});
