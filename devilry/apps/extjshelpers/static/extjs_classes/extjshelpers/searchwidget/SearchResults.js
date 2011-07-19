/** A panel containing multiple search results under a common title and store.
 *
 *      ------------------------
 *      | title                |
 *      ------------------------
 *      | result 1             |
 *      | result 2             |
 *      | result 3             |
 *      -----------------------|
 *
 * @xtype searchresults
 * */
Ext.define('devilry.extjshelpers.searchwidget.SearchResults', {
    extend: 'Ext.panel.Panel',
    alias: 'widget.searchresults',
    requires: ['devilry.extjshelpers.searchwidget.SearchResultItem'],
    cls: 'searchresults',
    hidden: true,
    config: {
        /**
         * @cfg
         * Editor url prefix (__Required__). The editor url for a specific
         * item is ``editorurlprefix+id``. Note that this means that editorurlprefix _must_
         * end with ``/``. _Required_.
         */
        editorurlprefix: undefined,

        /**
         * @cfg
         * Title of these search results. _Required_.
         */
        title: undefined,

        /**
         * @cfg
         * The ``Ext.data.store`` where the results are loaded from. _Required_.
         */
        store: undefined,

        /**
         * @cfg
         * Formatting template for the text rendered for each result item. _Required_.
         */
        rowformattpl: undefined,

        filterconfig: undefined,

    },

    constructor: function(config) {
        this.callParent([config]);
        var filterconfig = {
            type: undefined,
            shortcuts: new Object()
        };
        if(this.filterconfig) {
            Ext.apply(filterconfig, this.filterconfig);
        }
        this.filterconfig = filterconfig;
        this.pageSwitcherLabelTpl = Ext.create('Ext.XTemplate', '{from}-{to} of {total}');
        return this;
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            frame: false,
            hideHeaders: true,
            minButtonWidth: 0,

            fbar: [{
                xtype: 'button',
                text: '<',
                id: this.id + '-pageswitch-prevbtn',
                listeners: {
                    click: function() {
                        me.store.previousPage();
                    }
                }
            }, {
                xtype: 'component',
                html: 'something',
                id: this.id + '-pageswitch-label'
            }, {
                xtype: 'button',
                text: '>',
                id: this.id + '-pageswitch-nextbtn',
                listeners: {
                    click: function() {
                        me.store.nextPage();
                    }
                }
            }]
        });
        this.callParent(arguments);

        this.store.addListener('load', function(store, records, successful) {
            if(successful) {
                me.handleStoreLoadSuccess(records);
                me.updatePageSwitcher();
            } else {
                me.handleStoreLoadFailure();
            }
        });
    },

    updatePageSwitcher: function() {
        var from = this.store.pageSize * (this.store.currentPage-1);
        var visibleOnCurrentPage = this.store.getCount();
        var label = this.pageSwitcherLabelTpl.apply({
            total: this.store.getTotalCount(),
            from: from,
            to: from + visibleOnCurrentPage
        });
        this.getPageSwitcherLabel().update(label);

        this.getPreviousPageButton().hide();
        if(from > 0) {
            this.getPreviousPageButton().show();
        }
        this.getNextPageButton().hide();
        if(visibleOnCurrentPage == this.store.pageSize && (from+visibleOnCurrentPage) != this.store.getTotalCount()) {
            this.getNextPageButton().show();
        }
    },
    getPageSwitcherLabel: function() {
        return Ext.getCmp(this.id + '-pageswitch-label');
    },
    getPreviousPageButton: function() {
        return Ext.getCmp(this.id + '-pageswitch-prevbtn');
    },
    getNextPageButton: function() {
        return Ext.getCmp(this.id + '-pageswitch-nextbtn');
    },

    handleStoreLoadFailure: function() {
        //console.log('Failed to load store'); // TODO Better error handling
    },

    handleStoreLoadSuccess: function(records) {
        this.removeAll();
        var me = this;
        Ext.each(records, function(record, index) {
            me.addRecord(record, index);
        });
    },

    addRecord: function(record, index) {
        var searchresultitem = Ext.clone(this.resultitemConfig);
        Ext.apply(searchresultitem, {
            xtype: 'searchresultitem',
            recorddata: record.data,
            recordindex: index
        });
        this.add(searchresultitem);
    },


    search: function(parsedSearch) {
        if(parsedSearch.type && parsedSearch.type != this.filterconfig.type) {
            this.hide();
            return;
        }
        this.store.proxy.extraParams = parsedSearch.applyToExtraParams(this.store.proxy.extraParams, this.filterconfig.shortcuts);
        //console.log(this.store.proxy.extraParams);
        this.loadStore();
    },

    loadStore: function() {
        var me = this;
        this.store.load(function(records, operation, success) {
            if(success) {
                if(me.store.data.items.length == 0) {
                    me.hide();
                } else {
                    me.show();
                }
            } else {
                me.hide();
            }
        });
    }
});