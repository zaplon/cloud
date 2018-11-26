from django.core.files import File

from result.models import Result


def save_document(title, patient, file, user):
    F = File(open(file, mode='rb'))
    r = Result.objects.create(name=title, patient_id=patient, specialization=user.doctor.specializations.first(),
                              uploaded_by=user)
    r.file.save('%s.pdf' % title, F)