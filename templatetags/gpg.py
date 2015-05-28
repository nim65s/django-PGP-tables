# -*- coding: utf-8 -*-

from __future__ import division, unicode_literals

from django import template

register = template.Library()


@register.filter
def signatures(key, ksp):
    return ksp.key_signatures(key)


@register.filter
def signer(key, ksp):
    return ksp.key_signer(key)


@register.filter
def signed(key, ksp):
    return ksp.key_signed(key)


@register.filter
def stats(ksp):
    sigs, sigs_max = ksp.stats()
    return '%i / %i (%i%%)' % (sigs, sigs_max, 100 * sigs / sigs_max)
