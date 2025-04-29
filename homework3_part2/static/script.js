async function fetchApplications() {
    const response = await fetch('/api/applications');
    const data = await response.json();
    
    const appList = document.getElementById('applicationList');
    appList.innerHTML = "";

    data.applications.forEach(app => {
        let li = document.createElement('li');
        li.textContent = `${app.name} - ${app.address}, ${app.zipcode} (Status: ${app.status}, ID: ${app.app_id})`;
        appList.appendChild(li);
    });
}

async function submitApplication() {
    const name = document.getElementById('name').value;
    const address = document.getElementById('address').value;
    const zipcode = document.getElementById('zipcode').value;

    const response = await fetch('/api/submit_application', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, address, zipcode })
    });

    const data = await response.json();
    alert(data.message);
    fetchApplications();
}

async function checkStatus() {
    const appId = document.getElementById('statusAppId').value;
    const response = await fetch(`/api/status/${appId}`);
    const data = await response.json();
    
    const statusList = document.getElementById('statusList');
    statusList.innerHTML = "";

    if (data.application) {
        const app = data.application;
        let li = document.createElement('li');
        li.textContent = `Name: ${app.name}, Address: ${app.address}, Zipcode: ${app.zipcode}, Status: ${app.status}`;
        statusList.appendChild(li);
    } else {
        alert(data.message);
    }
}

async function changeStatus() {
    const appId = document.getElementById('changeAppId').value;
    const status = document.getElementById('statusSelect').value;
    const note = document.getElementById('note').value;

    const response = await fetch('/api/change_status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ app_id: appId, status, note })
    });

    const data = await response.json();
    alert(data.message);
    fetchApplications();
}

async function fetchNotes() {
    const appId = document.getElementById('notesAppId').value;
    const response = await fetch(`/api/notes/${appId}`);
    const data = await response.json();
    
    const notesList = document.getElementById('notesList');
    notesList.innerHTML = "";

    if (data.application) {
        const app = data.application;
        let li = document.createElement('li');
        li.textContent = `Notes for ${app.name}:`;
        notesList.appendChild(li);
        app.notes.forEach(note => {
            let li = document.createElement('li');
            li.textContent = `${note.date}: ${note.text}`;
            notesList.appendChild(li);
        });
    } else {
        alert(data.message);
    }
}

document.addEventListener("DOMContentLoaded", fetchApplications);