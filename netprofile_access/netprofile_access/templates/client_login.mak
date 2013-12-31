## -*- coding: utf-8 -*-
<%inherit file="netprofile_access:templates/client_base.mak"/>
<%block name="title">${_('Log In')}</%block>
<%block name="head">\
	<link rel="stylesheet" href="${req.static_url('netprofile_access:static/css/login.css')}" type="text/css" />
</%block>

<div class="container">
<form class="form-signin" role="form" method="post" action="${req.route_url('access.cl.login')}">
	<h2 class="form-signin-heading">${_('Log In')}</h2>
	<input type="hidden" id="csrf" name="csrf" value="${req.get_csrf()}" />
	<input type="text" class="form-control" placeholder="${_('User Name')}" required="required" autofocus="autofocus" id="user" name="user" title="${_('Enter your user name here')}" value="" maxlength="254" tabindex="1" autocomplete="off" />
	<input type="password" class="form-control" placeholder="${_('Password')}" required="required" id="pass" name="pass" title="${_('Enter your password here')}" value="" maxlength="254" tabindex="2" autocomplete="off" />
	<button type="submit" class="btn btn-lg btn-primary btn-block" id="submit" name="submit" title="${_('Log in to your account')}" tabindex="3">${_('Log In')}</button>
</form>
<form class="form-signin" role="form" method="get" action="${req.route_url('access.cl.login')}">
	<div class="input-group">
		<label class="input-group-addon" for="__locale">${_('Language')}</label>
		<select class="form-control chosen-select" id="__locale" name="__locale" tabindex="4">
% for lang in langs:
			<option label="${lang[1]}" value="${lang[0]}"\
% if lang[0] == cur_loc:
 selected="selected"\
% endif
>${lang[1]}</option>
% endfor
		</select>
		<span class="input-group-btn">
			<button type="submit" class="btn btn-default" id="lang_submit" title="${_('Change your current language')}">${_('Change')}</button>
		</span>
	</div>
	<div>
% if can_reg:
		<a href="${req.route_url('access.cl.register')}" id="register" class="btn btn-default" title="${_('Register new account')}" tabindex="5">${_('Register')}</a>
% endif
% if can_recover:
		<a href="${req.route_url('access.cl.restorepass')}" id="restorepass" class="btn btn-info pull-right" title="${_('Recover lost password via e-mail')}" tabindex="6">${_('Lost Password?')}</a>
% endif
	</div>
</form>
</div>
