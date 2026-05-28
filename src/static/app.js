document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const loginForm = document.getElementById("login-form");
  const logoutButton = document.getElementById("logout-button");
  const signupForm = document.getElementById("signup-form");
  const adminForm = document.getElementById("admin-form");
  const loginSection = document.getElementById("login-panel");
  const authStatus = document.getElementById("auth-status");
  const authUser = document.getElementById("auth-user");
  const signupContainer = document.getElementById("signup-container");
  const adminContainer = document.getElementById("admin-container");
  const adminTitle = document.getElementById("admin-form-title");
  const cancelEditButton = document.getElementById("cancel-edit");
  const messageDiv = document.getElementById("message");

  let authToken = localStorage.getItem("authToken") || "";
  let currentUser = null;
  let editingActivity = null;

  function setMessage(text, type = "info") {
    messageDiv.textContent = text;
    messageDiv.className = `message ${type}`;
    messageDiv.classList.remove("hidden");
  }

  function clearMessage() {
    messageDiv.className = "message hidden";
    messageDiv.textContent = "";
  }

  function clearSession() {
    authToken = "";
    currentUser = null;
    localStorage.removeItem("authToken");
    updateAuthUi();
    clearActivities();
  }

  function updateAuthUi() {
    const isLoggedIn = Boolean(currentUser);
    loginSection.classList.toggle("hidden", isLoggedIn);
    authStatus.classList.toggle("hidden", !isLoggedIn);
    signupContainer.classList.toggle("hidden", !isLoggedIn);
    adminContainer.classList.toggle(
      "hidden",
      !isLoggedIn || currentUser.role !== "admin"
    );

    if (isLoggedIn) {
      authUser.textContent = `${currentUser.name} (${currentUser.role})`;
    } else {
      authUser.textContent = "";
      resetAdminForm();
    }
  }

  function clearActivities() {
    activitySelect.innerHTML =
      '<option value="">-- Select an activity --</option>';
    activitiesList.innerHTML =
      "<p>Please log in to view activities and available actions.</p>";
  }

  async function apiFetch(path, options = {}) {
    const headers = new Headers(options.headers || {});

    if (authToken) {
      headers.set("Authorization", "Bearer " + authToken);
    }

    if (options.body && !headers.has("Content-Type")) {
      headers.set("Content-Type", "application/json");
    }

    return fetch(path, { ...options, headers });
  }

  function createTextElement(tagName, text, className = "") {
    const element = document.createElement(tagName);
    if (className) {
      element.className = className;
    }
    element.textContent = text;
    return element;
  }

  function createActionButton(label, className, onClick) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = className;
    button.textContent = label;
    button.addEventListener("click", onClick);
    return button;
  }

  async function fetchActivities() {
    if (!currentUser) {
      clearActivities();
      return;
    }

    try {
      const response = await apiFetch("/activities");
      if (response.status === 401) {
        clearSession();
        setMessage("Your session expired. Please log in again.", "error");
        return;
      }

      const activities = await response.json();
      if (!response.ok) {
        throw new Error(activities.detail || "Failed to load activities");
      }

      renderActivities(activities);
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  function renderActivities(activities) {
    activitiesList.innerHTML = "";
    activitySelect.innerHTML =
      '<option value="">-- Select an activity --</option>';

    Object.entries(activities).forEach(([name, details]) => {
      const card = document.createElement("div");
      card.className = "activity-card";

      card.appendChild(createTextElement("h4", name));
      card.appendChild(createTextElement("p", details.description));
      card.appendChild(
        createTextElement("p", `Schedule: ${details.schedule}`, "detail-row")
      );
      card.appendChild(
        createTextElement(
          "p",
          `Availability: ${details.spots_left} spots left`,
          "detail-row"
        )
      );

      if (currentUser.role === "admin") {
        card.appendChild(renderAdminCard(name, details));
      } else {
        card.appendChild(renderMemberCard(name, details));
      }

      activitiesList.appendChild(card);

      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      activitySelect.appendChild(option);
    });
  }

  function renderMemberCard(name, details) {
    const container = document.createElement("div");
    container.className = "participants-container";

    container.appendChild(
      createTextElement(
        "p",
        details.is_registered ? "You are registered." : "You are not registered.",
        "status-text"
      )
    );

    if (details.attendance_status) {
      container.appendChild(
        createTextElement(
          "p",
          `Attendance: ${details.attendance_status}`,
          "status-text"
        )
      );
    }

    if (details.is_registered) {
      container.appendChild(
        createActionButton("Unregister Me", "secondary-btn", async () => {
          await unregisterFromActivity(name);
        })
      );
    }

    return container;
  }

  function renderAdminCard(name, details) {
    const container = document.createElement("div");
    container.className = "participants-container";

    const actions = document.createElement("div");
    actions.className = "card-actions";
    actions.appendChild(
      createActionButton("Edit", "secondary-btn", () => startEditing(name, details))
    );
    actions.appendChild(
      createActionButton("Delete", "danger-btn", async () => {
        await deleteActivity(name);
      })
    );
    container.appendChild(actions);

    const participantsTitle = createTextElement("h5", "Participants");
    container.appendChild(participantsTitle);

    if (!details.participants.length) {
      container.appendChild(
        createTextElement("p", "No participants enrolled yet.", "status-text")
      );
      return container;
    }

    const list = document.createElement("ul");
    list.className = "participants-list";

    details.participants.forEach((email) => {
      const item = document.createElement("li");
      const row = document.createElement("div");
      row.className = "participant-row";

      const emailText = createTextElement("span", email, "participant-email");
      row.appendChild(emailText);

      const attendance = details.attendance[email] || "not marked";
      row.appendChild(
        createTextElement("span", attendance, "attendance-badge")
      );

      const buttonGroup = document.createElement("div");
      buttonGroup.className = "attendance-actions";
      buttonGroup.appendChild(
        createActionButton("Present", "small-btn", async () => {
          await updateAttendance(name, email, "present");
        })
      );
      buttonGroup.appendChild(
        createActionButton("Absent", "small-btn", async () => {
          await updateAttendance(name, email, "absent");
        })
      );

      row.appendChild(buttonGroup);
      item.appendChild(row);
      list.appendChild(item);
    });

    container.appendChild(list);
    return container;
  }

  function startEditing(name, details) {
    editingActivity = name;
    adminTitle.textContent = `Edit ${name}`;
    document.getElementById("admin-name").value = name;
    document.getElementById("admin-description").value = details.description;
    document.getElementById("admin-schedule").value = details.schedule;
    document.getElementById("admin-max-participants").value =
      details.max_participants;
    cancelEditButton.classList.remove("hidden");
  }

  function resetAdminForm() {
    editingActivity = null;
    adminTitle.textContent = "Manage Activities";
    adminForm.reset();
    cancelEditButton.classList.add("hidden");
  }

  async function unregisterFromActivity(activityName) {
    try {
      const response = await apiFetch(
        `/activities/${encodeURIComponent(activityName)}/unregister`,
        {
          method: "DELETE",
        }
      );
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Unable to unregister");
      }

      setMessage(result.message, "success");
      await fetchActivities();
    } catch (error) {
      setMessage(error.message, "error");
    }
  }

  async function deleteActivity(activityName) {
    try {
      const response = await apiFetch(
        `/activities/${encodeURIComponent(activityName)}`,
        {
          method: "DELETE",
        }
      );
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Unable to delete activity");
      }

      if (editingActivity === activityName) {
        resetAdminForm();
      }

      setMessage(result.message, "success");
      await fetchActivities();
    } catch (error) {
      setMessage(error.message, "error");
    }
  }

  async function updateAttendance(activityName, email, attendanceStatus) {
    try {
      const response = await apiFetch(
        `/activities/${encodeURIComponent(activityName)}/attendance`,
        {
          method: "PUT",
          body: JSON.stringify({ email, status: attendanceStatus }),
        }
      );
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Unable to update attendance");
      }

      setMessage(result.message, "success");
      await fetchActivities();
    } catch (error) {
      setMessage(error.message, "error");
    }
  }

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    clearMessage();

    try {
      const email = document.getElementById("login-email").value;
      const password = document.getElementById("login-password").value;
      const response = await fetch("/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const result = await response.json();
      if (!response.ok) {
        throw new Error(result.detail || "Login failed");
      }

      authToken = result.token;
      currentUser = result.user;
      localStorage.setItem("authToken", authToken);
      loginForm.reset();
      updateAuthUi();
      setMessage(`Logged in as ${currentUser.email}`, "success");
      await fetchActivities();
    } catch (error) {
      setMessage(error.message, "error");
    }
  });

  logoutButton.addEventListener("click", async () => {
    try {
      if (authToken) {
        await apiFetch("/auth/logout", { method: "POST" });
      }
    } finally {
      clearSession();
      setMessage("Logged out successfully.", "info");
    }
  });

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
      const activity = document.getElementById("activity").value;
      const response = await apiFetch(
        `/activities/${encodeURIComponent(activity)}/signup`,
        {
          method: "POST",
        }
      );
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Unable to sign up");
      }

      signupForm.reset();
      setMessage(result.message, "success");
      await fetchActivities();
    } catch (error) {
      setMessage(error.message, "error");
    }
  });

  adminForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    try {
      const payload = {
        name: document.getElementById("admin-name").value.trim(),
        description: document.getElementById("admin-description").value.trim(),
        schedule: document.getElementById("admin-schedule").value.trim(),
        max_participants: Number(
          document.getElementById("admin-max-participants").value
        ),
      };

      const isEditing = Boolean(editingActivity);
      const response = await apiFetch(
        isEditing
          ? `/activities/${encodeURIComponent(editingActivity)}`
          : "/activities",
        {
          method: isEditing ? "PUT" : "POST",
          body: JSON.stringify(payload),
        }
      );
      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.detail || "Unable to save activity");
      }

      resetAdminForm();
      setMessage(result.message, "success");
      await fetchActivities();
    } catch (error) {
      setMessage(error.message, "error");
    }
  });

  cancelEditButton.addEventListener("click", () => {
    resetAdminForm();
    clearMessage();
  });

  async function restoreSession() {
    updateAuthUi();

    if (!authToken) {
      clearActivities();
      return;
    }

    try {
      const response = await apiFetch("/auth/me");
      if (!response.ok) {
        throw new Error("Session expired");
      }

      currentUser = await response.json();
      updateAuthUi();
      await fetchActivities();
    } catch (error) {
      console.error("Error restoring session:", error);
      clearSession();
    }
  }

  clearActivities();
  restoreSession();
});
