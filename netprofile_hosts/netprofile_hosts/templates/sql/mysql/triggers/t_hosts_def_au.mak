## -*- coding: utf-8 -*-
<%inherit file="netprofile:templates/ddl_trigger.mak"/>\
<%block name="sql">\
	INSERT INTO `logs_data` (`login`, `type`, `action`, `data`)
	VALUES (@accesslogin, 4, 2, CONCAT_WS(" ",
		"Modified host",
		CONCAT("[ID ", NEW.hostid, "]")
	));
</%block>
