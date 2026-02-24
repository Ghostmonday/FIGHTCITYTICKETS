import { render, screen } from "@testing-library/react";
import BlogPostPage from "./page";
import * as seoData from "../../lib/seo-data";

// Mock the seo-data module
jest.mock("../../lib/seo-data", () => ({
  getBlogPostBySlug: jest.fn(),
  loadBlogPosts: jest.fn(() => []),
}));

// Mock next/navigation
jest.mock("next/navigation", () => ({
  notFound: jest.fn(),
}));

describe("BlogPostPage", () => {
  it("sanitizes structured data to prevent XSS", async () => {
    const mockPost = {
      title: "Test </script><script>alert(1)</script>",
      slug: "test-post",
      content: "This is a test post content.",
    };

    (seoData.getBlogPostBySlug as jest.Mock).mockReturnValue(mockPost);

    const jsx = await BlogPostPage({ params: Promise.resolve({ slug: "test-post" }) });
    const { container } = render(jsx);

    // Get the script content
    const scriptTag = container.querySelector('script[type="application/ld+json"]');
    expect(scriptTag).not.toBeNull();

    if (scriptTag) {
        const content = scriptTag.innerHTML;
        // Verify that the vulnerability is NOT present (no unescaped </script>)
        // This assertion should fail before the fix.
        expect(content).not.toContain("</script>");
    }
  });
});
