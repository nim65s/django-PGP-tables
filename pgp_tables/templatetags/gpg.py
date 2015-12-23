from django import template

register = template.Library()


@register.filter
def signatures(key, ksp):
    return key.signatures(ksp)


@register.filter
def signer(key, ksp):
    return key.n_signer(ksp)


@register.filter
def signed(key, ksp):
    return key.n_signed(ksp)


@register.filter
def to_do(key, ksp):
    return zip(ksp.keys.all(), key.signed_ksp(ksp), key.signer_ksp(ksp))


@register.filter
def stats(ksp):
    sigs, sigs_max = ksp.stats()
    return '%i / %i (%i%%)' % (sigs, sigs_max, 100 * sigs / sigs_max)
