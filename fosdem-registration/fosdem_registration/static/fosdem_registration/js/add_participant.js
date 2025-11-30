document.addEventListener("DOMContentLoaded", function() {

    const addButton = document.getElementById("add-form");
    const formContainer = document.getElementById("formset-container");
    const emptyForm = document.getElementById("empty-form")?.innerHTML;

    if (!addButton || !formContainer || !emptyForm) {
        console.error("Add participant JS: missing required elements");
        return;
    }

    addButton.addEventListener("click", function () {
        const totalFormsInput = document.getElementById("id_form-TOTAL_FORMS");
        let formIndex = parseInt(totalFormsInput.value);

        let newFormHtml = emptyForm.replace(/__prefix__/g, formIndex);

        let newFormDiv = document.createElement("div");
        newFormDiv.classList.add("participant-form");
        newFormDiv.innerHTML = newFormHtml;
        formContainer.appendChild(newFormDiv);

        totalFormsInput.value = formIndex + 1;
    });
});
