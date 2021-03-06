/**
 * @class NetProfile.view.ModelSelect
 * @extends Ext.form.field.Trigger
 */
Ext.define('NetProfile.view.ModelSelect', {
	extend: 'Ext.form.field.Trigger',
	alias: 'widget.modelselect',
	requires: [
		'Ext.ux.window.CenterWindow'
	],
	apiModule: null,
	apiClass: null,
	hiddenField: null,
	gridConfig: null,
	extraParams: null,
	showLink: true,
	trigger1Cls: 'x-form-clear-trigger',
	trigger2Cls: ' ',
	trigger3Cls: 'x-form-search-trigger',

	chooseText: 'Choose an object',

	initComponent: function()
	{
		if(!this.allowBlank)
		{
			this.trigger1Cls = this.trigger2Cls;
			this.onTrigger1Click = this.onTrigger2Click;
			this.trigger2Cls = undefined;
			this.onTrigger2Click = undefined;
		}
		if(!this.showLink)
		{
			this.trigger3Cls = undefined;
			this.onTrigger3Click = undefined;
		}
		else if(!this.allowBlank)
		{
			this.trigger2Cls = this.trigger3Cls;
			this.onTrigger2Click = this.onTrigger3Click;
			this.trigger3Cls = undefined;
			this.onTrigger3Click = undefined;
		}
		this.callParent(arguments);
	},
	onTrigger1Click: function(ev)
	{
		var form = this.up('form'),
			hf = form.down('field[name=' + this.hiddenField + ']');
		if(hf)
			hf.setValue('');
		else
			form.getRecord().set(this.hiddenField, '');

		this.setValue('');
	},
	onTrigger2Click: function(ev)
	{
		var sel_win = Ext.create('Ext.ux.window.CenterWindow', {
//			animateTarget: this,
			title: this.chooseText
		});

		var sel_grid_class = 'NetProfile.view.grid.'
			+ this.apiModule
			+ '.'
			+ this.apiClass;
		var form = this.up('form'),
			hf = form.down('field[name=' + this.hiddenField + ']');
		if(!hf)
			hf = this.hiddenField;
		var sel_grid_cfg = Ext.apply({
//		var sel_grid = Ext.create(sel_grid_class, {
			rowEditing: false,
			actionCol: false,
			selectRow: true,
			selectField: this,
			selectIdField: hf,
			extraParams: this.extraParams,
			stateful: false
		}, this.gridConfig || {});
		var sel_grid = Ext.create(sel_grid_class, sel_grid_cfg);

		sel_win.add(sel_grid);
		sel_win.show();
	},
	onTrigger3Click: function(ev)
	{
		var ff,
			store = NetProfile.StoreManager.getStore(
				this.apiModule,
				this.apiClass,
				null, true, true
			),
			hf = this.up('form').down('field[name=' + this.hiddenField + ']');

		if(!store)
			return false;
		if(!hf)
			hf = this.hiddenField;
		if(!hf)
			return false;
		hf = hf.getValue();
		if(!hf)
			return false;
		ff = { __ffilter: {} };
		ff.__ffilter[store.model.prototype.idProperty] = { eq: parseInt(hf) };
		store.load({
			params: ff,
			callback: function(recs, op, success)
			{
				var dp, pb, poly, apim, apic;
				poly = recs[0].get('__poly');
				if(poly)
				{
					apim = poly[0];
					apic = poly[1];
				}
				else
				{
					apim = this.apiModule;
					apic = this.apiClass;
				}

				pb = this.up('propbar');
				dp = NetProfile.view.grid[apim][apic].prototype.detailPane;
				if(success && pb && dp)
					pb.addRecordTab(apim, apic, dp, recs[0]);
			},
			scope: this,
			synchronous: false
		});
		return true;
	}
});

