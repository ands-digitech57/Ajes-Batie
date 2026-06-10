from django.core.exceptions import ValidationError

def validate_file_size(max_mb):
    def _validator(f):
        limit = max_mb * 1024 * 1024
        if f.size > limit:
            raise ValidationError(f'Le fichier est trop volumineux (max {max_mb}MB).')
    return _validator


def validate_file_extension(allowed_extensions):
    def _validator(f):
        name = getattr(f, 'name', '') or ''
        if not any(name.lower().endswith(ext) for ext in allowed_extensions):
            raise ValidationError(f'Extension de fichier non autorisee. Extensions autorisees: {", ".join(allowed_extensions)}')
    return _validator


def _validate_image(f):
    validate_file_size(5)(f)
    validate_file_extension(['.jpg', '.jpeg', '.png', '.gif'])(f)


def _validate_cv(f):
    validate_file_size(10)(f)
    validate_file_extension(['.pdf', '.docx', '.doc'])(f)


validate_image_file = _validate_image
validate_cv_file = _validate_cv
