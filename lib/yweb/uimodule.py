def show_error( E ):

    ''' return the error msg in list E '''

    return '<ul class="yerror">%s</ul>' % ''.join(['<li>%s</li>' % str(e) for e in E]) if E else ''
