const form = document.getElementById("todo-form");
const list = document.getElementById("todo-list");
const statusEl = document.getElementById("status");
const template = document.getElementById("todo-item-template");
const filterButtons = document.querySelectorAll(".filter");

let currentFilter = "all";

function setStatus(message) {
  statusEl.textContent = message;
}

async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    let errorMessage = "Request failed";
    try {
      const payload = await response.json();
      errorMessage = payload.error || errorMessage;
    } catch (_error) {
      // ignore JSON parsing failures for non-JSON responses
    }
    throw new Error(errorMessage);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

function renderTodos(todos) {
  list.innerHTML = "";
  if (!todos.length) {
    setStatus("No todos for this filter.");
    return;
  }

  setStatus(`${todos.length} todo(s) shown.`);

  todos.forEach((todo) => {
    const node = template.content.firstElementChild.cloneNode(true);
    const checkbox = node.querySelector(".toggle");
    const title = node.querySelector(".todo-title");
    const description = node.querySelector(".todo-description");
    const tags = node.querySelector(".todo-tags");
    const editButton = node.querySelector(".edit");
    const deleteButton = node.querySelector(".delete");

    checkbox.checked = todo.done;
    title.textContent = todo.title;
    description.textContent = todo.description || "No description";
    tags.textContent = todo.tags ? `Tags: ${todo.tags}` : "No tags";

    if (todo.done) {
      node.classList.add("done");
    }

    checkbox.addEventListener("change", async () => {
      try {
        await request(`/api/todos/${todo.id}/toggle`, { method: "PATCH" });
        await refresh();
      } catch (error) {
        setStatus(error.message);
      }
    });

    editButton.addEventListener("click", async () => {
      const nextTitle = window.prompt("Update title:", todo.title);
      if (!nextTitle || !nextTitle.trim()) {
        return;
      }
      const nextDescription = window.prompt("Update description:", todo.description || "");
      const nextTags = window.prompt("Update tags:", todo.tags || "");

      try {
        await request(`/api/todos/${todo.id}`, {
          method: "PUT",
          body: JSON.stringify({
            title: nextTitle.trim(),
            description: (nextDescription || "").trim(),
            tags: (nextTags || "").trim(),
            done: checkbox.checked,
          }),
        });
        await refresh();
      } catch (error) {
        setStatus(error.message);
      }
    });

    deleteButton.addEventListener("click", async () => {
      const confirmed = window.confirm("Delete this todo?");
      if (!confirmed) {
        return;
      }

      try {
        await request(`/api/todos/${todo.id}`, { method: "DELETE" });
        await refresh();
      } catch (error) {
        setStatus(error.message);
      }
    });

    list.appendChild(node);
  });
}

async function refresh() {
  try {
    const todos = await request(`/api/todos?status=${currentFilter}`);
    renderTodos(todos);
  } catch (error) {
    setStatus(error.message);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = document.getElementById("title").value.trim();
  const description = document.getElementById("description").value.trim();
  const tags = document.getElementById("tags").value.trim();

  if (!title) {
    setStatus("Title is required.");
    return;
  }

  try {
    await request("/api/todos", {
      method: "POST",
      body: JSON.stringify({ title, description, tags }),
    });
    form.reset();
    await refresh();
  } catch (error) {
    setStatus(error.message);
  }
});

filterButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    filterButtons.forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    currentFilter = button.dataset.filter;
    await refresh();
  });
});

refresh();
