const API_BASE_URL = "";

let token = localStorage.getItem("token");
let currentPage = 0;
const limit = 5;

const authSection = document.getElementById("authSection");
const appSection = document.getElementById("appSection");
const logoutBtn = document.getElementById("logoutBtn");
const messageBox = document.getElementById("messageBox");
const taskList = document.getElementById("taskList");
const pageInfo = document.getElementById("pageInfo");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");

function showMessage(msg, isError = false) {
    messageBox.innerHTML = isError ? `<i class="fa-solid fa-circle-exclamation"></i> ${msg}` : `<i class="fa-solid fa-circle-check"></i> ${msg}`;
    messageBox.className = `toast show ${isError ? "error" : "success"}`;
    
    // Clear any existing timeouts to prevent race conditions
    if(window.toastTimeout) clearTimeout(window.toastTimeout);
    
    window.toastTimeout = setTimeout(() => {
        messageBox.classList.remove("show");
    }, 3000);
}

function checkAuth() {
    if (token) {
        authSection.style.display = "none";
        appSection.style.display = "block";
        logoutBtn.style.display = "block";
        fetchTasks();
    } else {
        authSection.style.display = "flex";
        appSection.style.display = "none";
        logoutBtn.style.display = "none";
    }
}

document.getElementById("registerForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("regEmail").value;
    const password = document.getElementById("regPassword").value;
    
    try {
        const res = await fetch(`${API_BASE_URL}/register`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
            showMessage("Registration successful! Please login.");
            document.getElementById("registerForm").reset();
        } else {
            showMessage(data.detail || "Registration failed", true);
        }
    } catch (err) {
        showMessage("Server error", true);
    }
});

document.getElementById("loginForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("loginEmail").value;
    const password = document.getElementById("loginPassword").value;
    
    try {
        const res = await fetch(`${API_BASE_URL}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
            token = data.access_token;
            localStorage.setItem("token", token);
            document.getElementById("loginForm").reset();
            checkAuth();
            showMessage("Logged in successfully!");
        } else {
            showMessage(data.detail || "Login failed", true);
        }
    } catch (err) {
        showMessage("Server error", true);
    }
});

logoutBtn.addEventListener("click", () => {
    token = null;
    localStorage.removeItem("token");
    checkAuth();
});

document.getElementById("createTaskForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("taskTitle").value;
    
    try {
        const res = await fetch(`${API_BASE_URL}/tasks`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ title })
        });
        if (res.ok) {
            document.getElementById("createTaskForm").reset();
            fetchTasks();
            showMessage("Task created!");
        } else {
            showMessage("Failed to create task", true);
        }
    } catch (err) {
        showMessage("Server error", true);
    }
});

async function fetchTasks() {
    let filter = document.querySelector('input[name="filter"]:checked').value;
    let url = `${API_BASE_URL}/tasks?skip=${currentPage * limit}&limit=${limit}`;
    if (filter === "completed") url += "&completed=true";
    if (filter === "active") url += "&completed=false";

    try {
        const res = await fetch(url, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
            const tasks = await res.json();
            renderTasks(tasks);
            pageInfo.textContent = `Page ${currentPage + 1}`;
            prevBtn.disabled = currentPage === 0;
            nextBtn.disabled = tasks.length < limit;
        } else if (res.status === 401) {
            logoutBtn.click();
        }
    } catch (err) {
        showMessage("Error fetching tasks", true);
    }
}

function renderTasks(tasks) {
    taskList.innerHTML = "";
    tasks.forEach(task => {
        const li = document.createElement("li");
        if (task.completed) li.classList.add("completed");
        
        const contentDiv = document.createElement("div");
        contentDiv.className = "task-content";
        
        const checkbox = document.createElement("div");
        checkbox.className = "task-checkbox";
        checkbox.innerHTML = '<i class="fa-solid fa-check"></i>';
        checkbox.onclick = () => toggleTask(task.id, !task.completed);
        
        const titleSpan = document.createElement("span");
        titleSpan.className = "task-title";
        titleSpan.textContent = task.title;
        
        contentDiv.appendChild(checkbox);
        contentDiv.appendChild(titleSpan);
        
        const actionsDiv = document.createElement("div");
        actionsDiv.className = "task-actions";
        
        const delBtn = document.createElement("button");
        delBtn.innerHTML = '<i class="fa-solid fa-trash"></i>';
        delBtn.className = "btn-delete";
        delBtn.title = "Delete Task";
        delBtn.onclick = () => deleteTask(task.id);
        
        actionsDiv.appendChild(delBtn);
        
        li.appendChild(contentDiv);
        li.appendChild(actionsDiv);
        taskList.appendChild(li);
    });
}

async function toggleTask(id, completed) {
    try {
        await fetch(`${API_BASE_URL}/tasks/${id}`, {
            method: "PUT",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ completed })
        });
        fetchTasks();
    } catch (err) {
        showMessage("Error updating task", true);
    }
}

async function deleteTask(id) {
    try {
        await fetch(`${API_BASE_URL}/tasks/${id}`, {
            method: "DELETE",
            headers: { "Authorization": `Bearer ${token}` }
        });
        fetchTasks();
    } catch (err) {
        showMessage("Error deleting task", true);
    }
}

document.querySelectorAll('input[name="filter"]').forEach(radio => {
    radio.addEventListener('change', () => {
        currentPage = 0;
        fetchTasks();
    });
});

prevBtn.addEventListener('click', () => {
    if (currentPage > 0) {
        currentPage--;
        fetchTasks();
    }
});

nextBtn.addEventListener('click', () => {
    currentPage++;
    fetchTasks();
});

// Init
checkAuth();
