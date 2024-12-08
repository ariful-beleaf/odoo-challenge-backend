/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';
import { jsonrpc } from "@web/core/network/rpc_service";

publicWidget.registry.EventCustom = publicWidget.Widget.extend({
    selector: '.event-custom',

    /**
     * @override
     */
    start: async function () {
        await this._super(...arguments);
        let eventRow = this.el.querySelector('#custom-events-row');
        
        if (eventRow) {
            try {
                eventRow.innerHTML = '<div class="loading">Loading...</div>';
                
                const result = await jsonrpc('/custom/events');
                console.log(result)
                const events = result.events;
                console.log(events)
                
                let html = '';
                if (events && events.length) {
                    events.forEach(event => {
                        html += `
                            <div class="col-lg-3">
                                <div class="card">
                                    <div class="card-body">
                                        <h5 class="card-title">${event.name}</h5>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                } else {
                    html = '<div class="col-12 text-center">No events found</div>';
                }
                
                eventRow.innerHTML = html;

            } catch (error) {
                console.error('Failed to load events:', error);
                eventRow.innerHTML = '<div class="col-12 text-center text-danger">Failed to load events</div>';
            }
        }
    },



});

export default publicWidget.registry.EventCustom;
