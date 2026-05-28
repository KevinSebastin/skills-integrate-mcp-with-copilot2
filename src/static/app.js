document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const adminForm = document.getElementById("admin-form");
  const adminTitleInput = document.getElementById("admin-title");
  const adminDescriptionInput = document.getElementById("admin-description");
  const adminScheduleInput = document.getElementById("admin-schedule");
  const adminCapacityInput = document.getElementById("admin-capacity");
  const editingActivityNameInput = document.getElementById(
    "editing-activity-name"
  );
  const adminSubmitButton = document.getElementById("admin-submit");
  const adminCancelButton = document.getElementById("admin-cancel");
  const adminMessageDiv = document.getElementById("admin-message");

  let currentActivities = {};

  function escapeHtml(value) {
    return String(value).replace(
      /[&<>"']/g,
      (character) =>
        (
          {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
          }[character]
        )
    );
  }

  function showMessage(target, message, type) {
    target.textContent = message;
    target.className = `message ${type}`;

    if (target.hideTimeoutId) {
      clearTimeout(target.hideTimeoutId);
    }

    target.hideTimeoutId = setTimeout(() => {
      target.className = "hidden";
    }, 5000);
  }

  function formatError(result, fallbackMessage) {
    if (!result) {
      return fallbackMessage;
    }

    if (typeof result.detail === "string") {
      return result.detail;
    }

    if (Array.isArray(result.detail)) {
      return result.detail
        .map((item) => item.msg || item.message || fallbackMessage)
        .join(", ");
    }

    return fallbackMessage;
  }

  function resetActivitySelect() {
    activitySelect.innerHTML =
      '<option value="">-- Select an activity --</option>';
  }

  function resetAdminForm() {
    adminForm.reset();
    editingActivityNameInput.value = "";
    adminSubmitButton.textContent = "Create Activity";
    adminCancelButton.classList.add("hidden");
  }

  function loadActivityIntoAdminForm(activityName) {
    const activity = currentActivities[activityName];

    if (!activity) {
      showMessage(adminMessageDiv, "Activity not found.", "error");
      return;
    }

    editingActivityNameInput.value = activityName;
    adminTitleInput.value = activityName;
    adminDescriptionInput.value = activity.description;
    adminScheduleInput.value = activity.schedule;
    adminCapacityInput.value = activity.max_participants;
    adminSubmitButton.textContent = "Update Activity";
    adminCancelButton.classList.remove("hidden");
    showMessage(adminMessageDiv, `Editing ${activityName}`, "info");
    adminTitleInput.focus();
  }

  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      currentActivities = activities;
      activitiesList.innerHTML = "";
      resetActivitySelect();

      const entries = Object.entries(activities);

      if (entries.length === 0) {
        activitiesList.innerHTML = "<p><em>No activities available right now.</em></p>";
        return;
      }

      entries.forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const safeName = escapeHtml(name);
        const safeDescription = escapeHtml(details.description);
        const safeSchedule = escapeHtml(details.schedule);
        const spotsLeft =
          details.max_participants - details.participants.length;

        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
                <h5>Participants:</h5>
                <ul class="participants-list">
                  ${details.participants
                    .map(
                      (email) =>
                        `<li><span class="participant-email">${escapeHtml(
                          email
                        )}</span><button class="delete-btn" data-activity="${safeName}" data-email="${escapeHtml(
                          email
                        )}" type="button">❌</button></li>`
                    )
                    .join("")}
                </ul>
              </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${safeName}</h4>
          <p>${safeDescription}</p>
          <p><strong>Schedule:</strong> ${safeSchedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
          <div class="activity-admin-actions">
            <button class="secondary-btn edit-activity-btn" data-activity="${safeName}" type="button">
              Edit
            </button>
            <button class="danger-btn delete-activity-btn" data-activity="${safeName}" type="button">
              Delete
            </button>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  async function handleUnregister(button) {
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );
      const result = await response.json();

      if (response.ok) {
        showMessage(messageDiv, result.message, "success");
        fetchActivities();
        return;
      }

      showMessage(
        messageDiv,
        formatError(result, "An error occurred"),
        "error"
      );
    } catch (error) {
      showMessage(messageDiv, "Failed to unregister. Please try again.", "error");
      console.error("Error unregistering:", error);
    }
  }

  async function handleDeleteActivity(button) {
    const activity = button.getAttribute("data-activity");

    if (!window.confirm(`Delete ${activity}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `/admin/activities/${encodeURIComponent(activity)}`,
        {
          method: "DELETE",
        }
      );
      const result = await response.json();

      if (response.ok) {
        if (editingActivityNameInput.value === activity) {
          resetAdminForm();
        }

        showMessage(adminMessageDiv, result.message, "success");
        fetchActivities();
        return;
      }

      showMessage(
        adminMessageDiv,
        formatError(result, "Failed to delete activity."),
        "error"
      );
    } catch (error) {
      showMessage(
        adminMessageDiv,
        "Failed to delete activity. Please try again.",
        "error"
      );
      console.error("Error deleting activity:", error);
    }
  }

  activitiesList.addEventListener("click", (event) => {
    const button = event.target.closest("button");

    if (!button) {
      return;
    }

    if (button.classList.contains("delete-btn")) {
      handleUnregister(button);
      return;
    }

    if (button.classList.contains("edit-activity-btn")) {
      loadActivityIntoAdminForm(button.getAttribute("data-activity"));
      return;
    }

    if (button.classList.contains("delete-activity-btn")) {
      handleDeleteActivity(button);
    }
  });

  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );
      const result = await response.json();

      if (response.ok) {
        showMessage(messageDiv, result.message, "success");
        signupForm.reset();
        fetchActivities();
        return;
      }

      showMessage(
        messageDiv,
        formatError(result, "An error occurred"),
        "error"
      );
    } catch (error) {
      showMessage(messageDiv, "Failed to sign up. Please try again.", "error");
      console.error("Error signing up:", error);
    }
  });

  adminForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const activityToEdit = editingActivityNameInput.value;
    const payload = {
      title: adminTitleInput.value,
      description: adminDescriptionInput.value,
      schedule: adminScheduleInput.value,
      capacity: Number(adminCapacityInput.value),
    };
    const isEditing = Boolean(activityToEdit);
    const url = isEditing
      ? `/admin/activities/${encodeURIComponent(activityToEdit)}`
      : "/admin/activities";

    try {
      const response = await fetch(url, {
        method: isEditing ? "PUT" : "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      const result = await response.json();

      if (response.ok) {
        showMessage(adminMessageDiv, result.message, "success");
        resetAdminForm();
        fetchActivities();
        return;
      }

      showMessage(
        adminMessageDiv,
        formatError(result, "Failed to save activity."),
        "error"
      );
    } catch (error) {
      showMessage(
        adminMessageDiv,
        "Failed to save activity. Please try again.",
        "error"
      );
      console.error("Error saving activity:", error);
    }
  });

  adminCancelButton.addEventListener("click", () => {
    resetAdminForm();
    adminMessageDiv.className = "hidden";
  });

  fetchActivities();
});
