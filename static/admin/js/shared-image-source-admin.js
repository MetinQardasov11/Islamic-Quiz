(function () {
    function toggleElement(element, shouldShow) {
        if (!element) {
            return;
        }
        element.style.display = shouldShow ? '' : 'none';
    }

    function syncImageSourceFields(scope) {
        (scope || document).querySelectorAll('[data-image-source-selector]').forEach(function (selectField) {
            if (selectField.closest('.inline-related')) {
                return;
            }
            const row = selectField.closest('.form-row');
            const targetField = selectField.getAttribute('data-image-target');
            const fileTargetField = selectField.getAttribute('data-image-file-target');
            const urlRow = document.querySelector('.form-row.field-' + targetField);
            const fileRow = document.querySelector('.form-row.field-' + fileTargetField);
            const mode = selectField.value || 'url';

            toggleElement(row, true);
            toggleElement(urlRow, mode === 'url');
            toggleElement(fileRow, mode === 'file');
        });

        (scope || document).querySelectorAll('.inline-related').forEach(function (inlineForm) {
            inlineForm.querySelectorAll('[data-image-source-selector]').forEach(function (selectField) {
                const row = selectField.closest('.form-row');
                const targetField = selectField.getAttribute('data-image-target');
                const fileTargetField = selectField.getAttribute('data-image-file-target');
                const urlRow = inlineForm.querySelector('.field-' + targetField);
                const fileRow = inlineForm.querySelector('.field-' + fileTargetField);
                const mode = selectField.value || 'url';

                toggleElement(row, true);
                toggleElement(urlRow, mode === 'url');
                toggleElement(fileRow, mode === 'file');
            });
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.body.addEventListener('change', function (event) {
            if (event.target && event.target.matches('[data-image-source-selector]')) {
                syncImageSourceFields(document);
            }
        });
        document.body.addEventListener('formset:added', function () {
            syncImageSourceFields(document);
        });
        syncImageSourceFields(document);
    });
})();
