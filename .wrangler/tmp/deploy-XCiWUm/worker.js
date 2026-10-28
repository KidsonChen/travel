var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// worker/worker.js
var worker_default = {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type"
        }
      });
    }
    const url = new URL(request.url);
    const path = url.pathname;
    if (path === "/api/expenses" && request.method === "GET") {
      return getExpenses(request, env);
    }
    if (path === "/api/expenses" && request.method === "POST") {
      return addExpense(request, env);
    }
    if (path.startsWith("/api/expenses/") && request.method === "DELETE") {
      return deleteExpense(request, env, path);
    }
    if (path === "/api/migrate" && request.method === "POST") {
      return migrateFromLocalStorage(request, env);
    }
    return new Response("Not Found", { status: 404 });
  }
};
async function getExpenses(request, env) {
  try {
    const { results } = await env.D1.prepare("SELECT * FROM expenses ORDER BY created_at DESC").all();
    return jsonResponse(results);
  } catch (error) {
    console.error("Error fetching expenses:", error);
    return jsonResponse({ error: "Failed to fetch expenses" }, 500);
  }
}
__name(getExpenses, "getExpenses");
async function addExpense(request, env) {
  try {
    const body = await request.json();
    if (!body.name || !body.amount || !body.payer || !body.shared) {
      return jsonResponse({ error: "Missing required fields" }, 400);
    }
    const expense = {
      name: body.name,
      amount: body.amount,
      payer: body.payer,
      note: body.note || "",
      shared: JSON.stringify(body.shared),
      date: body.date || (/* @__PURE__ */ new Date()).toLocaleDateString("zh-TW")
    };
    const result = await env.D1.prepare(
      "INSERT INTO expenses (name, amount, payer, note, shared, date) VALUES (?, ?, ?, ?, ?, ?)"
    ).run(expense.name, expense.amount, expense.payer, expense.note, expense.shared, expense.date);
    return jsonResponse({ id: result.meta.last_row_id, ...expense }, 201);
  } catch (error) {
    console.error("Error adding expense:", error);
    return jsonResponse({ error: "Failed to add expense" }, 500);
  }
}
__name(addExpense, "addExpense");
async function deleteExpense(request, env, path) {
  try {
    const id = parseInt(path.split("/").pop());
    if (isNaN(id)) {
      return jsonResponse({ error: "Invalid expense ID" }, 400);
    }
    await env.D1.prepare("DELETE FROM expenses WHERE id = ?").run(id);
    return jsonResponse({ success: true });
  } catch (error) {
    console.error("Error deleting expense:", error);
    return jsonResponse({ error: "Failed to delete expense" }, 500);
  }
}
__name(deleteExpense, "deleteExpense");
async function migrateFromLocalStorage(request, env) {
  try {
    const body = await request.json();
    const expenses = body.expenses || [];
    if (!Array.isArray(expenses)) {
      return jsonResponse({ error: "Invalid expenses format" }, 400);
    }
    let count = 0;
    for (const expense of expenses) {
      await env.D1.prepare(
        "INSERT INTO expenses (name, amount, payer, note, shared, date) VALUES (?, ?, ?, ?, ?, ?)"
      ).run(
        expense.name,
        expense.amount,
        expense.payer,
        expense.note || "",
        JSON.stringify(expense.shared),
        expense.date
      );
      count++;
    }
    return jsonResponse({ migrated: count, total: expenses.length });
  } catch (error) {
    console.error("Error during migration:", error);
    return jsonResponse({ error: "Migration failed" }, 500);
  }
}
__name(migrateFromLocalStorage, "migrateFromLocalStorage");
function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*"
    }
  });
}
__name(jsonResponse, "jsonResponse");
export {
  worker_default as default
};
//# sourceMappingURL=worker.js.map
