document.addEventListener('DOMContentLoaded', function() {
    const groupSelect = document.getElementById('group');
    const studentSelect = document.getElementById('student');
    
    if (!groupSelect || !studentSelect) return;
    
    groupSelect.addEventListener('change', function() {
        const groupId = this.value;
        
        if (!groupId) {
            studentSelect.innerHTML = '<option value="" selected>Сначала выберите группу</option>';
            studentSelect.disabled = true;
            return;
        }
        
        // Загружаем студентов выбранной группы
        fetch(`/api/students/?group_id=${groupId}`)
            .then(response => {
                if (!response.ok) throw new Error('Ошибка сети');
                return response.json();
            })
            .then(data => {
                studentSelect.innerHTML = '<option value="" disabled selected>Выберите студента</option>';
                
                if (data.students && data.students.length > 0) {
                    data.students.forEach(student => {
                        const option = document.createElement('option');
                        option.value = student.id;
                        option.textContent = student.student_name;  // ИЗМЕНИЛ: было 'name', должно быть 'student_name'
                        studentSelect.appendChild(option);
                    });
                    studentSelect.disabled = false;
                } else {
                    studentSelect.innerHTML = '<option value="" selected>В этой группе нет студентов</option>';
                    studentSelect.disabled = true;
                }
            })
            .catch(error => {
                console.error('Ошибка загрузки студентов:', error);
                studentSelect.innerHTML = '<option value="" selected>Ошибка загрузки</option>';
                studentSelect.disabled = true;
            });
    });
});