def query_param_enabled(query_params, name):
    return query_params.get(name, "false").lower() == "true"


def apply_related_modes(queryset, query_params, *, select=(), prefetch=()):
    if query_param_enabled(query_params, "select") and select:
        queryset = queryset.select_related(*select)

    if (
        query_param_enabled(query_params, "prefetch")
        or query_param_enabled(query_params, "prefetch_select")
    ) and prefetch:
        queryset = queryset.prefetch_related(*prefetch)

    if query_param_enabled(query_params, "prefetch_select") and select:
        queryset = queryset.prefetch_related(*select)

    return queryset
