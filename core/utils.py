from django.utils.text import slugify

AZ_MAP = str.maketrans({
    "ə": "e", "Ə": "e",
    "ı": "i", "I": "i", "İ": "i",
    "ö": "o", "Ö": "o",
    "ü": "u", "Ü": "u",
    "ş": "s", "Ş": "s",
    "ç": "c", "Ç": "c",
    "ğ": "g", "Ğ": "g",
})


def az_slugify(value: str) -> str:
    """Azərbaycan hərflərini latın ekvivalentinə çevirib slug yaradır."""
    return slugify((value or "").translate(AZ_MAP)) or "item"


def unique_slug(model, base: str, instance_pk=None) -> str:
    slug = base[:170]
    counter = 2
    qs = model.objects.all()
    if instance_pk:
        qs = qs.exclude(pk=instance_pk)
    while qs.filter(slug=slug).exists():
        slug = f"{base[:165]}-{counter}"
        counter += 1
    return slug
