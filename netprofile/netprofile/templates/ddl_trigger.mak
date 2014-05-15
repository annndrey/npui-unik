## -*- coding: utf-8 -*-
<%namespace name="ddl" module="netprofile.db.ddl" import="ddl_fmt" inheritable="True"/>
% if dialect.name == 'mysql':
CREATE TRIGGER ${trigger}
${trigger.when.upper()} ${trigger.event.upper()}
ON ${table}
FOR EACH ROW
BEGIN
% elif dialect.name == 'pgsql':
CREATE FUNCTION ${trigger.name + '_func()'}
RETURNS TRIGGER AS $$
BEGIN
% endif
<%block name="sql"/>\
% if dialect.name == 'mysql':
END
% elif dialect.name == 'pgsql':
END;
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER ${trigger}
${trigger.when.upper()} ${trigger.event.upper()}
ON ${table}
FOR EACH ROW
EXECUTE PROCEDURE
${trigger.name + '_func()'};
% endif

