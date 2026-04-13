function buildDom() {
  document.body.innerHTML = `
    <main>
      <form id="todo-form">
        <input id="title" type="text" />
        <textarea id="description"></textarea>
        <input id="tags" type="text" />
        <button type="submit">Add Todo</button>
      </form>
      <button type="button" data-filter="all" class="filter active">All</button>
      <button type="button" data-filter="open" class="filter">Open</button>
      <button type="button" data-filter="done" class="filter">Done</button>
      <p id="status"></p>
      <ul id="todo-list"></ul>
      <template id="todo-item-template">
        <li class="todo-item">
          <input type="checkbox" class="toggle" />
          <strong class="todo-title"></strong>
          <p class="todo-description"></p>
          <small class="todo-tags"></small>
          <button type="button" class="edit">Edit</button>
          <button type="button" class="delete">Delete</button>
        </li>
      </template>
    </main>
  `;
}

async function flushAsync() {
  await new Promise((resolve) => setTimeout(resolve, 0));
  await new Promise((resolve) => setTimeout(resolve, 0));
}

describe("frontend todo app", () => {
  beforeEach(() => {
    jest.resetModules();
    buildDom();
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [],
    });
    global.prompt = jest.fn();
    global.confirm = jest.fn(() => true);
  });

  test("loads todos on startup", async () => {
    require("../../src/static/app.js");
    await flushAsync();

    expect(global.fetch).toHaveBeenCalledWith(
      "/api/todos?status=all",
      expect.objectContaining({
        headers: { "Content-Type": "application/json" },
      })
    );
    expect(document.getElementById("status").textContent).toBe("No todos for this filter.");
  });

  test("shows validation when title is empty", async () => {
    require("../../src/static/app.js");
    await flushAsync();

    document.getElementById("title").value = "   ";
    document.getElementById("todo-form").dispatchEvent(
      new Event("submit", { bubbles: true, cancelable: true })
    );

    expect(document.getElementById("status").textContent).toBe("Title is required.");
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });
});
