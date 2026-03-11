function loadStudents() {
    const groupSelect = document.getElementById('group-select');
    const studentSelect = document.getElementById('student-select');
    const selectedGroup = groupSelect.value;
    
    if (!selectedGroup) {
        studentSelect.innerHTML = '<option value="">-- Сначала выберите группу --</option>';
        return;
    }
    studentSelect.innerHTML = '<option value="">Загрузка...</option>';
    fetch(`/student_list/${selectedGroup}/`)
        .then(response => response.json())
        .then(data => {
            if (data.length > 0) {
                let options = '<option value="">-- Выберите студента --</option>';
                data.forEach(student => {
                    options += `<option value="${student.id}">${student.student_name}</option>`;
                });  
                studentSelect.innerHTML = options;
            } else {
                studentSelect.innerHTML = '<option value="">В этой группе нет студентов</option>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            studentSelect.innerHTML = '<option value="">Ошибка загрузки</option>';
        });
}