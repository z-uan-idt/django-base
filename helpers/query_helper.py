from django.db import models


class PostgresqlJsonField(models.JSONField):
    def from_db_value(self, value, expression, connection):
        return value


class SubqueryJson(models.Subquery):
    template = "(SELECT row_to_json(_subquery) FROM (%(subquery)s) _subquery)"
    output_field = PostgresqlJsonField()


class SubqueryJsonAgg(models.Subquery):
    template = "(SELECT array_to_json(coalesce(array_agg(row_to_json(_subquery)), array[]::json[])) FROM (%(subquery)s) _subquery)"
    output_field = PostgresqlJsonField()

    def __init__(self, queryset, alias=None, flat=False):
        self.flat = flat

        if self.flat:
            queryset = queryset.values_list(alias, flat=True)

        super().__init__(queryset)

    def as_sql(self, compiler, connection, template=None):
        if self.flat:
            self.extra["value"] = f"_subquery.{self.queryset.query.values[0]}"
        else:
            self.extra["value"] = "row_to_json(_subquery)"

        return super().as_sql(compiler, connection, template)


class UnaccentVN(models.Func):
    function = "unaccent_vn"
    template = "translate(%(expressions)s, 'áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựíìỉĩịýỳỷỹỵđÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÍÌỈĨỊÝỲỶỸỴĐ', 'aaaaaaaaaaaaaaaaaeeeeeeeeeeeooooooooooooooooouuuuuuuuuuuiiiiiyyyyydAAAAAAAAAAAAAAAAAEEEEEEEEEEEOOOOOOOOOOOOOOOOOUUUUUUUUUUUIIIIIYYYYYD')"
    output_field = models.CharField()