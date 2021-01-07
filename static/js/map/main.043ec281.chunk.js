(this["webpackJsonpdtp-map"]=this["webpackJsonpdtp-map"]||[]).push([[0],{67:function(e,t,a){e.exports=a(89)},72:function(e,t,a){},77:function(e,t,a){},89:function(e,t,a){"use strict";a.r(t);var n=a(2),r=a.n(n),c=a(60),i=a.n(c),o=a(92),s=(a(72),"https://beta.dtp-stat.ru/api"),l="https://beta.dtp-stat.ru",u="https://2ab4410dbc6440a7ab3bfd0963c217d5@o412018.ingest.sentry.io/5288112",d=a(7),m=a(16),f=a.n(m),p=a(4),v=a(61),g=a.n(v);var b,y,h=function(e,t){var a;return null===(a=b)||void 0===a||a.abort(),b=new AbortController,fetch("".concat(s,"/stat/?center_point=").concat(e[1],"+").concat(e[0],"&scale=").concat(t),{signal:b.signal}).then((function(e){return e.json()}))},E={},w=function(e,t){var a;return null===(a=y)||void 0===a||a.abort(),y=new AbortController,Promise.all(e.map((function(e){return function(e,t,a){var n,r=null===(n=E[a])||void 0===n?void 0:n[t];return r?Promise.resolve(r):fetch("".concat(s,"/dtp_load/?year=").concat(t,"&region_slug=").concat(a,"&format=json"),{signal:e}).then((function(e){return e.json()})).then((function(e){return E[a]||(E[a]={}),E[a][t]=e,e}))}(y.signal,e,t)})))},S=p.types.model("DateValue",{start_date:p.types.string,end_date:p.types.string}),j=p.types.model("DateFilter",{name:p.types.literal("date"),label:p.types.string,default_value:S,value:p.types.optional(S,{start_date:"",end_date:""})}).actions((function(e){return{afterCreate:function(){e.value=e.default_value},setValue:function(t){e.value=Object(p.cast)(t),Object(p.getRoot)(e).onDatesChanged()}}})),N=p.types.model("ParticipantItem",{preview:p.types.string,value:p.types.number,icon:p.types.string,default:p.types.boolean,selected:!1}).actions((function(e){return{afterCreate:function(){e.selected=e.default},setSelected:function(t){e.selected=t},selectOne:function(){e.selected||(Object(p.getParent)(e).forEach((function(t){t.setSelected(t===e)})),Object(p.getRoot)(e).onFiltersChanged())}}})),k=p.types.model("ParticipantsFilter",{name:p.types.literal("participant_categories"),label:p.types.string,multiple:p.types.boolean,values:p.types.array(N)}),O=p.types.model("SeverityItem",{preview:p.types.string,value:p.types.number,color:p.types.string,disabled:p.types.boolean,default:p.types.boolean,selected:!1}).actions((function(e){return{afterCreate:function(){e.selected=e.default},changeSelection:function(){e.selected=!e.selected,Object(p.getRoot)(e).onFiltersChanged()}}})),C=p.types.model("SeverityFilter",{name:p.types.literal("severity"),label:p.types.string,multiple:p.types.boolean,values:p.types.array(O)}),F=p.types.model("RegionFilter",{name:p.types.literal("region"),label:p.types.string,values:p.types.array(p.types.number)}),_=p.types.model("CategoryFilterValue",{preview:p.types.string,value:p.types.number,default:!1,selected:!1}).actions((function(e){return{toggle:function(){e.selected=!e.selected,Object(p.getRoot)(e).onFiltersChanged()},reset:function(){e.selected=e.default}}})),x=p.types.model("CategoryFilter",{name:p.types.literal("category"),key:p.types.string,label:p.types.string,values:p.types.array(_)}).actions((function(e){return{reset:function(){e.values.forEach((function(e){return e.reset()})),Object(p.getRoot)(e).onFiltersChanged()},navigate:function(){Object(p.getRoot)(e).filterStore.setCurrentKey(e.key)}}}));p.types.union(k,j,C,F,x);function D(e){switch(e.name){case"date":return j.create(e);case"participant_categories":return k.create(e);case"severity":return C.create(e);case"region":return F.create(e);case"category":return x.create(e)}}var A=p.types.model("FilterStore",{filters:p.types.array(p.types.union(k,j,C,F,x)),visible:!0,search:"",currentKey:p.types.maybeNull(p.types.string)}).actions((function(e){function t(t){e.filters.clear(),e.filters=Object(p.cast)(t.map(D))||[]}var a=Object(p.flow)(f.a.mark((function e(){return f.a.wrap((function(e){for(;;)switch(e.prev=e.next){case 0:return e.next=2,fetch("".concat(s,"/filters")).then((function(e){return e.json()}));case 2:t(e.sent);case 4:case"end":return e.stop()}}),e)})));return{setFilters:t,updateStreets:function(t){if(t){var a=e.filters.find((function(e){return"street"===e.key}));if(a){var n=new Set(t.filter((function(e){return e.street})).map((function(e){return e.street}))),r=new Set(a.values.filter((function(e){return e.selected})).map((function(e){return e.preview})));r.forEach((function(e){n.add(e)}));var c=Array.from(n);c.sort();var i=c.map((function(e){return _.create({preview:e,value:-1,selected:r.has(e)})}));a.values=Object(p.cast)(i)}}},loadFilters:a,setCurrentKey:function(t){e.currentKey=t},setVisible:function(t){e.visible=t},setSearch:function(t){e.search=t}}})).views((function(e){return{get date(){var t=e.filters.filter((function(e){return"date"===e.name}));return null===t||void 0===t?void 0:t[0]},get startDate(){var e;return null===(e=this.date)||void 0===e?void 0:e.value.start_date},get endDate(){var e;return null===(e=this.date)||void 0===e?void 0:e.value.end_date}}})),I=a(64),L=a(50),R=a(51),P=a.n(R),z="#18334A",H="#8d99a5",M="#586c7c",B="#FF001A",U="#FFB81F",K=function(e){var t=e.name,a=e.color;return r.a.createElement("svg",{className:"icon icon-".concat(t),style:{fill:a||""}},r.a.createElement("use",{xlinkHref:"svg/sprite.svg#".concat(t)}))},T=function(e){var t=e.datetime.toLocaleString("ru",{year:"numeric",month:"numeric",day:"numeric",hour:"numeric",minute:"numeric"}),a="".concat(e.injured," \u0447\u0435\u043b\u043e\u0432\u0435\u043a \u043f\u043e\u0441\u0442\u0440\u0430\u0434\u0430\u043b\u0438");e.injured%10===1&&11!==e.injured&&(a="".concat(e.injured," \u0447\u0435\u043b\u043e\u0432\u0435\u043a \u043f\u043e\u0441\u0442\u0440\u0430\u0434\u0430\u043b"));var n="".concat(e.dead," \u0447\u0435\u043b\u043e\u0432\u0435\u043a \u043f\u043e\u0433\u0438\u0431\u043b\u0438");return e.dead%10===1&&11!==e.dead&&(n="".concat(e.dead," \u0447\u0435\u043b\u043e\u0432\u0435\u043a \u043f\u043e\u0433\u0438\u0431")),r.a.createElement(r.a.Fragment,null,r.a.createElement("div",{className:"balloon-header"},r.a.createElement("h4",{className:"subtitle1"},e.categoryName)),r.a.createElement("div",{className:"balloon-body"},r.a.createElement("p",{className:"body3"},t),r.a.createElement("p",{className:"body3"},e.address),e.injured>0&&r.a.createElement("p",{className:"subtitle3",style:{color:U}},a),e.dead>0&&r.a.createElement("p",{className:"subtitle3",style:{color:B}},n)),r.a.createElement("div",{className:"balloon-footer"},r.a.createElement("a",{className:"btn-light",href:"".concat(l,"/dtp/").concat(e.id),target:"_blank",rel:"noopener noreferrer"},"\u041f\u043e\u0434\u0440\u043e\u0431\u043d\u043e\u0441\u0442\u0438 \u0414\u0422\u041f")))},V={0:"svg/circle-0.svg",1:"svg/circle-1.svg",3:"svg/circle-3.svg",4:"svg/circle-4.svg",default:"svg/circle-default.svg"},W={1:"#FFB81F",3:"#FF7F24",4:"#FF001A"},Z=p.types.model("MapStore",{center:p.types.array(p.types.number),zoom:1}).actions((function(e){var t=null,a=null,n=null;function c(t,a){var n=e.zoom;e.center=Object(p.cast)(t),e.zoom=a,Object(p.getRoot)(e).onBoundsChanged(a,n)}var i=function(e){var t,n=a.objects.getById(e);n&&(n.properties.balloonContentBody=P.a.renderToStaticMarkup((t={id:n.properties.id,address:n.properties.address,categoryName:n.properties.category_name,dead:n.properties.dead,datetime:new Date(n.properties.datetime),injured:n.properties.injured},r.a.createElement("div",{className:"balloon"},r.a.createElement(T,t),r.a.createElement(K,{name:"pointer"})))),a.objects.balloon.open(e))},o=function(e){e.properties.balloonContentBody=P.a.renderToStaticMarkup(T({id:e.properties.id,address:e.properties.address,categoryName:e.properties.category_name,dead:e.properties.dead,datetime:new Date(e.properties.datetime),injured:e.properties.injured})),s(e.id)},s=function(e){var t=new URLSearchParams(document.location.search);t.set("active-obj",e),window.history.pushState(null,"","?".concat(t.toString()))},l=function(){var e=new URLSearchParams(document.location.search);e.delete("active-obj"),window.history.pushState(null,"","?".concat(e.toString()))};return{setMap:function(e){t=e,(a=new window.ymaps.ObjectManager({clusterize:!0,groupByCoordinates:!0,showInAlphabeticalOrder:!0,clusterDisableClickZoom:!0,clusterIconLayout:"default#pieChart"})).objects.events.add("click",(function(e){i(e.get("objectId"))})),a.objects.balloon.events.add("userclose",(function(){l()})),a.objects.balloon.events.add("open",(function(e){s(e.get("objectId"))})),a.clusters.balloon.events.add("close",(function(){l()})),a.clusters.state.events.add("change",(function(){o(a.clusters.state.get("activeObject"))})),a.clusters.balloon.events.add("close",(function(){l()})),(n=new window.ymaps.Heatmap([],{radius:15,dissipating:!1,opacity:.5,intensityOfMidpoint:.5,gradient:{0:"rgba(126, 171, 85, 0.0)",.2:"rgba(126, 171, 85, 0.6)",.4:"rgba(255, 254, 85, 0.7)",.6:"rgba(245, 193, 66, 0.8)",.8:"rgba(223, 130, 68, 0.9)",1:"rgba(176, 36, 24, 1)"}})).setMap(t,{}),t.geoObjects.add(a),c(t.getCenter(),t.getZoom())},getMap:function(){return t},updateBounds:c,drawPoints:function(e){a.removeAll(),n.setData([]);var t=e.map((function(e){return{type:"Feature",id:(t=e).id,geometry:{type:"Point",coordinates:[t.point.latitude,t.point.longitude]},properties:Object(I.a)({},t,{clusterCaption:t.datetime.split("T")[0],visible:!0}),options:{iconLayout:"default#image",iconImageHref:V[t.severity],iconImageSize:[10,10],iconImageOffset:[-5,-5],iconColor:W[t.severity]}};var t}));a.add(t);var r=new URLSearchParams(window.location.search).get("active-obj");r&&i(r)},drawHeat:function(e){a.removeAll();var t=e.map((function(e){return{id:(t=e).id,type:"Feature",geometry:{type:"Point",coordinates:[t.point.latitude,t.point.longitude]},properties:{weight:t.severity}};var t}));n.setData(t)},setFilter:function(e){a.setFilter((function(t){return e(t.properties)}))}}})),J=p.types.model("Area",{id:p.types.string,name:p.types.string,parentId:p.types.string,parentName:p.types.maybeNull(p.types.string)}),Y=p.types.model("AreaStatistics",{count:p.types.number,injured:p.types.number,dead:p.types.number}),$=p.types.model("AreaStore",{area:p.types.maybeNull(J),statistics:p.types.maybeNull(Y)}).actions((function(e){return{loadArea:Object(p.flow)(f.a.mark((function t(a,n){var r,c,i,o,s,l;return f.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return t.prev=0,t.next=3,h(a,n);case 3:if(i=t.sent,u=i,0!==Object.keys(u).length){t.next=6;break}return t.abrupt("return");case 6:o=J.create({id:i.region_slug,name:i.region_name,parentId:i.parent_region_slug,parentName:i.parent_region_name}),s=o.id!==(null===(r=e.area)||void 0===r?void 0:r.id),l=o.parentId!==(null===(c=e.area)||void 0===c?void 0:c.parentId),e.area=o,s&&Object(p.getRoot)(e).onAreaChanged(),l&&Object(p.getRoot)(e).onParentAreaChanged(),t.next=18;break;case 14:if(t.prev=14,t.t0=t.catch(0),"AbortError"===t.t0.name){t.next=18;break}throw t.t0;case 18:case"end":return t.stop()}var u}),t,null,[[0,14]])}))),setStatistics:function(t){e.statistics=Object(p.cast)(t)}}})),q=function(e,t){for(var a=[],n=parseInt(e.split("-")[0]),r=parseInt(t.split("-")[0]),c=n;c<=r;c++)a.push(c);return a},G=p.types.model({accs:p.types.frozen([])}).actions((function(e){return{loadTrafficAccidents:Object(p.flow)(f.a.mark((function t(a,n,r){var c,i;return f.a.wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return(c=Object(p.getRoot)(e)).incLoading(),t.prev=2,t.next=5,w(q(a,n),r);case 5:i=t.sent,e.accs=i.flat().filter((function(e){return e.point&&e.datetime>=a&&e.datetime<=n})),c.onTrafficAccidentsLoaded(),t.next=14;break;case 10:if(t.prev=10,t.t0=t.catch(2),"AbortError"===t.t0.name){t.next=14;break}throw t.t0;case 14:return t.prev=14,c.decLoading(),t.finish(14);case 17:case"end":return t.stop()}}),t,null,[[2,10,14,17]])})))}})),Q=p.types.model("RootStore",{filterStore:A,mapStore:Z,areaStore:$,trafficAccidentStore:G,loadingCount:0}).actions((function(e){var t=!1,a=!1,n=Object(p.flow)(f.a.mark((function n(){return f.a.wrap((function(n){for(;;)switch(n.prev=n.next){case 0:return v(),n.next=3,e.filterStore.loadFilters();case 3:g(),b(),a=!0,t&&(l(),r());case 7:case"end":return n.stop()}}),n)}))),r=function(){var t=e.mapStore,a=t.center,n=t.zoom;e.areaStore.loadArea(a,n)},c=function(){var t=e.areaStore,a=e.filterStore,n=e.trafficAccidentStore;t.area&&n.loadTrafficAccidents(a.startDate,a.endDate,t.area.parentId)},i=function(){var t=e.trafficAccidentStore.accs,a=e.areaStore.area;if(a){var n=(a.id===a.parentId?t:t.filter((function(e){return e.region_slug===a.id}))).filter(o());e.areaStore.setStatistics({count:n.length,injured:n.reduce((function(e,t){return e+t.injured}),0),dead:n.reduce((function(e,t){return e+t.dead}),0)})}},o=function(){var t=function(e){var t,a=[],n=Object(L.a)(e.filter((function(e){return"date"!==e.name})));try{for(n.s();!(t=n.n()).done;){var r=t.value,c=r.values.filter((function(e){return e.selected})).map((function(e){return-1===e.value?e.preview:e.value}));a.push({id:r.key||r.name,values:c})}}catch(i){n.e(i)}finally{n.f()}return a}(e.filterStore.filters.slice());return function(e){return function(e,t){var a,n=Object(L.a)(t);try{var r=function(){var t=a.value,n=e[t.id],r=t.values;if(0===r.length)return"continue";if(Array.isArray(n)){if(!n.some((function(e){return r.includes(e)})))return{v:!1}}else if(!r.includes(n))return{v:!1}};for(n.s();!(a=n.n()).done;){var c=r();switch(c){case"continue":continue;default:if("object"===typeof c)return c.v}}}catch(i){n.e(i)}finally{n.f()}return!0}(e,t)}},s=function(){if(e.mapStore.zoom>=14)e.mapStore.setFilter(o()),e.mapStore.drawPoints(e.trafficAccidentStore.accs);else{var t=e.trafficAccidentStore.accs.filter(o());e.mapStore.drawHeat(t)}},l=function(){var e=new URLSearchParams(document.location.search);u(e),d(e),m(e),window.history.pushState(null,"","?".concat(e.toString()))},u=function(t){var a=e.mapStore,n=a.center,r=a.zoom;t.set("center","".concat(n[0],":").concat(n[1])),t.set("zoom",String(r))},d=function(t){var a=e.filterStore.filters.find((function(e){return"date"===e.name})).value;t.set("start_date",a.start_date),t.set("end_date",a.end_date)},m=function(t){e.filterStore.filters.filter((function(e){return"date"!==e.name})).forEach((function(e){var a=e.key||e.name;t.delete(a);var n=e.values.filter((function(e){return e.selected}));n.length>0&&t.set(a,n.map((function(e){return"street"===a?e.preview:String(e.value)})).join(";"))}))},v=function(){var t,a=new URLSearchParams(document.location.search),n=null===(t=a.get("center"))||void 0===t?void 0:t.split(":"),r=n?[parseFloat(n[0]),parseFloat(n[1])]:[55.76,37.64],c=a.get("zoom"),i=c?parseInt(c,10):9;e.mapStore.center=Object(p.cast)(r),e.mapStore.zoom=i},g=function(){var t=new URLSearchParams(document.location.search),a=e.filterStore.filters.find((function(e){return"date"===e.name})),n=t.get("start_date"),r=t.get("end_date");n&&r&&(a.value={start_date:n,end_date:r})},b=function(){var t=new URLSearchParams(document.location.search);e.filterStore.filters.filter((function(e){return"date"!==e.name})).forEach((function(e){var a=e.key||e.name,n=t.get(a);if(n){var r=n.split(";");e.values.forEach((function(e){var t="street"===a?e.preview:String(e.value);e.selected=r.includes(t)}))}}))},y=function(){var t=new URLSearchParams(document.location.search),a=e.filterStore.filters.find((function(e){return"street"===e.key})),n=t.get("street");if(n){var r=n.split(";");a.values.forEach((function(e){e.selected=r.includes(e.preview)}))}};return{afterCreate:n,onBoundsChanged:function(e,n){t=!0,a&&(l(),r(),(e>=14&&n<14||e<14&&n>=14)&&s())},onAreaChanged:function(){i()},onParentAreaChanged:function(){c()},onTrafficAccidentsLoaded:function(){var t=e.trafficAccidentStore.accs;e.filterStore.updateStreets(t),y(),i(),s()},onDatesChanged:function(){l(),c()},onFiltersChanged:function(){l(),i(),e.mapStore.zoom>=14?e.mapStore.setFilter(o()):s()},incLoading:function(){e.loadingCount+=1},decLoading:function(){e.loadingCount-=1}}})).create({filterStore:{},mapStore:{},areaStore:{},trafficAccidentStore:{}});g()(Q);var X=r.a.createContext(Q);function ee(){return r.a.useContext(X)}var te=Object(d.a)((function(){var e=ee();return r.a.createElement("div",{className:e.loadingCount>0?"loader visible":"loader"})})),ae=(a(77),Object(d.a)((function(){var e=ee().mapStore,t=Object(n.useCallback)((function(t){var a=t.originalEvent,n=a.newCenter,r=a.newZoom,c=a.newBounds;e.updateBounds(n,r,c)}),[e]);return r.a.useEffect((function(){window.ymaps.ready(["Heatmap"]).then((function(){var a=e.center,n=e.zoom;e.setMap(new window.ymaps.Map("map",{center:a,zoom:n,controls:[]},{avoidFractionalZoom:!0})),e.getMap().events.add("boundschange",t)}))}),[e,t]),r.a.createElement("div",{id:"map"})}))),ne=a(54),re=(a(78),a(79),a(52)),ce=a(57),ie=a(42),oe=a(41),se=a(28),le=a(40),ue=a(53),de=function(e){return Object(ie.a)(e,"yyyy-MM-dd")},me=function(e){var t="dd.MM.yyyy";return"".concat(Object(ie.a)(e.startDate,t)," - ").concat(Object(ie.a)(e.endDate,t))},fe=function(e){var t=Object(oe.a)(new Date,e),a=Object(ie.a)(t,"LLLL",{locale:ue.a});return{label:a[0].toLocaleUpperCase("ru")+a.substring(1),range:function(){return{startDate:Object(se.a)(t),endDate:Object(le.a)(t)}}}},pe=function(){for(var e=[],t=(new Date).getFullYear(),a=1;a<=2;a++)e.push(fe(a));for(var n=function(t){e.push({label:t.toString(),range:function(){return{startDate:new Date(t,0,1),endDate:new Date(t,11,31)}}})},r=t;r>t-6;r--)n(r);return e.push({label:"\u0417\u0430 \u0432\u0441\u0451 \u0432\u0440\u0435\u043c\u044f",range:function(){return{startDate:new Date(t-5,0,1),endDate:new Date}}}),Object(re.createStaticRanges)(e)}(),ve=Object(d.a)((function(e){var t=e.filter,a={startDate:Object(ce.a)(t.value.start_date),endDate:Object(ce.a)(t.value.end_date),key:"selection"},n=r.a.useState(!1),c=Object(ne.a)(n,2),i=c[0],o=c[1],s=r.a.useState(a),l=Object(ne.a)(s,2),u=l[0],d=l[1];return r.a.createElement("div",null,r.a.createElement("div",{className:"inputWrap"},r.a.createElement("input",{type:"text",className:"input",onFocus:function(e){return o(!0)},readOnly:!0,value:me(a)}),r.a.createElement("svg",{className:"icon icon-calendar"},r.a.createElement("use",{xlinkHref:"svg/sprite.svg#calendar"}))),i&&r.a.createElement("div",{className:"date-wrap"},r.a.createElement(re.DateRangePicker,{locale:ue.a,onChange:function(e){d(e.selection),e.selection.endDate>e.selection.startDate&&(t.setValue({start_date:de(e.selection.startDate),end_date:de(e.selection.endDate)}),o(!1))},showDateDisplay:!1,months:2,ranges:[u],rangeColors:[M],inputRanges:[],staticRanges:pe,fixedHeight:!0,direction:"horizontal"}),r.a.createElement("div",{className:"date-bottom"},r.a.createElement("button",{className:"btn-light",onClick:function(e){o(!1)}},"\u041e\u0442\u043c\u0435\u043d\u0430"))))})),ge=Object(d.a)((function(e){return r.a.createElement("div",{className:"participant-filter"},e.values.map((function(e){return r.a.createElement("button",{key:e.value,className:e.selected?"participant-item active":"participant-item",tabIndex:0,onClick:e.selectOne},r.a.createElement("object",{type:"image/svg+xml",data:"".concat(l).concat(e.icon),"aria-label":e.preview}),r.a.createElement("p",{className:"subtitle3"},e.preview))})))})),be=Object(d.a)((function(e){var t=e.values;return r.a.createElement("div",null,t.map((function(e){return r.a.createElement("label",{key:e.value,className:"severity-item",tabIndex:0},r.a.createElement("input",{type:"checkbox",checked:e.selected,disabled:e.disabled,onChange:e.changeSelection}),r.a.createElement("span",{className:"checkmark"},r.a.createElement("svg",{className:"icon icon-check"},r.a.createElement("use",{xlinkHref:"svg/sprite.svg#check"}))),r.a.createElement("div",{className:"severity-color",style:{background:e.disabled?H:e.color}}),r.a.createElement("p",{className:"body1",style:{color:e.disabled?H:z}},e.preview))})))})),ye=Object(d.a)((function(e){e.values;return r.a.createElement("div",{className:"category-item__draw",tabIndex:0},r.a.createElement("svg",{className:"icon icon-edit"},r.a.createElement("use",{xlinkHref:"svg/sprite.svg#edit"})),r.a.createElement("button",{className:"btn-rect"},"\u0412\u044b\u0434\u0435\u043b\u0438\u0442\u044c"))})),he=function(e){var t=e.filter;switch(t.name){case"date":return r.a.createElement(ve,{filter:t});case"participant_categories":return r.a.createElement(ge,t);case"severity":return r.a.createElement(be,t);case"region":return r.a.createElement(ye,t);default:return null}},Ee=Object(d.a)((function(e){var t=e.filter;return t.values.some((function(e){return e.selected}))?r.a.createElement("div",{className:"category-tag active"},r.a.createElement("button",{className:"btn-rect",onClick:function(e){return t.navigate()}},r.a.createElement("span",null,t.label)),r.a.createElement("button",{className:"btn-decline",onClick:function(e){return t.reset()}},r.a.createElement("svg",{className:"icon icon-decline"},r.a.createElement("use",{xlinkHref:"svg/sprite.svg#decline"})))):r.a.createElement("div",{className:"category-tag"},r.a.createElement("button",{className:"btn-rect",onClick:function(e){return t.navigate()}},r.a.createElement("span",null,t.label)))})),we=Object(d.a)((function(){var e=ee().filterStore,t=e.filters,a=t.filter((function(e){return"category"!==e.name})),n=t.filter((function(e){return"category"===e.name}));return r.a.createElement("div",{className:"filter-panel"},a.map((function(e){return r.a.createElement("div",{key:e.name,className:"filter-item"},r.a.createElement("p",{className:"subtitle2"},e.label),r.a.createElement(he,{filter:e}))})),r.a.createElement("div",{className:"filter-item"},r.a.createElement("p",{className:"subtitle2"},"\u0424\u0438\u043b\u044c\u0442\u0440\u044b"),r.a.createElement("div",{className:"category-filter"},n.map((function(e){return r.a.createElement(Ee,{key:e.key,filter:e})})))),r.a.createElement("button",{className:"btn-hideFilter",onClick:function(t){return e.setVisible(!1)}},r.a.createElement("svg",{className:"icon icon-arrow-up"},r.a.createElement("use",{xlinkHref:"svg/sprite.svg#arrow-up"})),r.a.createElement("span",null,"\u0421\u043a\u0440\u044b\u0442\u044c")))})),Se=Object(d.a)((function(){var e=ee().filterStore,t=e.filters,a=t.find((function(e){return"date"===e.name})),n=(t.filter((function(e){var t;return null===(t=e.values)||void 0===t?void 0:t.some((function(e){return e.selected!==e.default}))}))||[]).map((function(e){return e.label})).join(", ");return r.a.createElement("div",{className:"filter-panel-hidden"},r.a.createElement("div",{className:"filter-item"},r.a.createElement("p",{className:"subtitle2"},a.label),r.a.createElement(ve,{filter:a})),n&&r.a.createElement("div",{className:"filter-item"},r.a.createElement("p",{className:"subtitle2"},"\u0410\u043a\u0442\u0438\u0432\u043d\u044b\u0435 \u0444\u0438\u043b\u044c\u0442\u0440\u044b"),r.a.createElement("div",{className:"category-filter"},n)),r.a.createElement("button",{className:"btn-hideFilter",onClick:function(t){return e.setVisible(!0)}},r.a.createElement("svg",{className:"icon icon-arrow-up"},r.a.createElement("use",{xlinkHref:"svg/sprite.svg#arrow-up"})),r.a.createElement("span",null,"\u041f\u043e\u043a\u0430\u0437\u0430\u0442\u044c")))})),je=Object(d.a)((function(){var e=ee().filterStore,t=e.filters.find((function(t){return t.key===e.currentKey}));return r.a.createElement("div",{className:"filter-header"},r.a.createElement("button",{className:"btn-back",onClick:function(t){e.setCurrentKey(null),e.setSearch("")}},r.a.createElement("svg",{className:"icon icon-arrow-back"},r.a.createElement("use",{xlinkHref:"svg/sprite.svg#arrow-back"})),r.a.createElement("span",null,t.label)),r.a.createElement("div",{className:"inputWrap"},r.a.createElement("input",{type:"text",className:"input",placeholder:"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 \u043d\u0430\u0440\u0443\u0448\u0435\u043d\u0438\u044f",value:e.search,onChange:function(t){return e.setSearch(t.target.value)}}),r.a.createElement("button",{className:"btn-search"},r.a.createElement("svg",{className:"icon icon-search"},r.a.createElement("use",{xlinkHref:"svg/sprite.svg#search"})))))})),Ne=Object(d.a)((function(e){var t=e.value;return r.a.createElement("label",{className:"category-value severity-item",tabIndex:0},r.a.createElement("input",{type:"checkbox",checked:t.selected,onChange:function(e){return t.toggle()}}),r.a.createElement("span",{className:"checkmark"},r.a.createElement("svg",{className:"icon icon-check"},r.a.createElement("use",{xlinkHref:"svg/sprite.svg#check"}))),r.a.createElement("span",{className:"value-preview body1"},t.preview))})),ke=Object(d.a)((function(){var e=ee().filterStore,t=e.filters.find((function(t){return t.key===e.currentKey})),a=e.search.toLowerCase();return r.a.createElement("div",{className:"filter-panel-category"},r.a.createElement(je,null),r.a.createElement("div",{className:"panel-content"},t.values.filter((function(e){return e.preview.toLowerCase().includes(a)})).map((function(e){return r.a.createElement(Ne,{key:-1===e.value?e.preview:e.value,value:e})}))))})),Oe=Object(d.a)((function(){var e=ee().filterStore;return 0===e.filters.length?null:e.visible?e.currentKey?r.a.createElement(ke,null):r.a.createElement(we,null):r.a.createElement(Se,null)})),Ce=Object(d.a)((function(){var e=ee().areaStore,t=e.area,a=e.statistics;return t?r.a.createElement("div",{className:"info-panel-wrap"},r.a.createElement("div",{className:"info-panel"},r.a.createElement("h3",{className:"h3"},t.name||"\xa0"),r.a.createElement("p",{className:"subtitle2",style:{color:H}},"\u0414\u0422\u041f"),r.a.createElement("p",{className:"subtitle2",style:{color:H}},"\u041f\u043e\u0441\u0442\u0440\u0430\u0434\u0430\u043b\u0438"),r.a.createElement("p",{className:"subtitle2",style:{color:H}},"\u041f\u043e\u0433\u0438\u0431\u043b\u0438"),r.a.createElement("p",{className:"body2",style:{color:H}},t.parentName),r.a.createElement("h3",{className:"h3",style:{color:z}},a?a.count:"-"),r.a.createElement("h3",{className:"h3",style:{color:U}},a?a.injured:"-"),r.a.createElement("h3",{className:"h3",style:{color:B}},a?a.dead:"-"))):null})),Fe=function(){return r.a.createElement(X.Provider,{value:Q},r.a.createElement(te,null),r.a.createElement(ae,null),r.a.createElement("div",{className:"ui-layer"},r.a.createElement(Oe,null),r.a.createElement(Ce,null)))};Boolean("localhost"===window.location.hostname||"[::1]"===window.location.hostname||window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));o.a({dsn:u}),i.a.render(r.a.createElement(r.a.StrictMode,null,r.a.createElement(Fe,null)),document.getElementById("root")),"serviceWorker"in navigator&&navigator.serviceWorker.ready.then((function(e){e.unregister()})).catch((function(e){console.error(e.message)}))}},[[67,1,2]]]);
//# sourceMappingURL=main.043ec281.chunk.js.map