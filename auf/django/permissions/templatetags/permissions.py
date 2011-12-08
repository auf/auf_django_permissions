from django import template

register = template.Library()


class IfHasPermNode(template.Node):

    def __init__(self, perm, obj, nodelist_true, nodelist_false):
        self.perm = template.Variable(perm)
        self.obj = template.Variable(obj)
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        if 'user' in context:
            user = context['user']
        else:
            user = context['request'].user
        perm = self.perm.resolve(context)
        obj = self.obj.resolve(context)
        if user.has_perm(perm, obj):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


class WithPermsNode(template.Node):

    def __init__(self, obj, var, nodelist):
        self.obj = template.Variable(obj)
        self.var = var
        self.nodelist = nodelist

    def render(self, context):
        if 'user' in context:
            user = context['user']
        else:
            user = context['request'].user
        obj = self.obj.resolve(context)
        context.update({self.var: PermWrapper(user, obj)})
        output = self.nodelist.render(context)
        context.pop()
        return output


class PermWrapper(object):

    def __init__(self, user, obj):
        self.user = user
        self.obj = obj

    def __getitem__(self, perm):
        return self.user.has_perm(perm, self.obj)


@register.tag
def ifhasperm(parser, token):
    bits = token.split_contents()[1:]
    if len(bits) != 2:
        raise template.TemplateSyntaxError("%r tag requires two arguments" %
                                           token.contents.split()[0])
    perm, obj = bits
    nodelist_true = parser.parse(('else', 'endifhasperm'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifhasperm',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return IfHasPermNode(perm, obj, nodelist_true, nodelist_false)

@register.tag
def withperms(parser, token):
    bits = token.split_contents()[1:]
    if len(bits) != 3 or bits[1] != 'as':
        raise template.TemplateSyntaxError("%r tag takes two arguments separated by 'as'" %
                                           token.contents.split()[0])
    obj = bits[0]
    var = bits[2]
    nodelist = parser.parse(('endwithperms',))
    parser.delete_first_token()
    return WithPermsNode(obj, var, nodelist)
