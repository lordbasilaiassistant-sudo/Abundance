/* Cited dataset → visible arithmetic. Everything outside these tabs is static HTML. */
(() => {
  const $ = id => document.getElementById(id);
  const tabs = Array.from(document.querySelectorAll('[data-resource]'));
  const format = (n, digits = 0) => n.toLocaleString('en-US', {maximumFractionDigits: digits, minimumFractionDigits: digits});
  let resources;
  function show(key) {
    const r = resources[key];
    tabs.forEach(tab => {
      const selected = tab.dataset.resource === key;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    $('resource-panel').setAttribute('aria-labelledby', `tab-${key}`);
    ['kicker','title','description','ratio','suffix','caveat'].forEach(field => $('resource-' + field).textContent = r[field]);
    $('ratio-caption').textContent = r.caption;
    $('supply-label').textContent = r.supplyLabel;
    $('supply-value').textContent = r.supplyValue;
    $('reference-label').textContent = r.referenceLabel;
    $('reference-value').textContent = r.referenceValue;
    $('reference-bar').style.width = r.referencePercent + '%';
    $('unit-label').textContent = r.unit;
    $('comparison').hidden = key === 'output';
    $('resource-source').textContent = r.source.source_name + ' · ' + r.source.year + ' ↗';
    $('resource-source').href = r.source.source_url;
    $('reference-source').href = r.reference.source_url;
    $('reference-source').textContent = r.reference.source_name + ' ↗';
  }
  fetch('data/essentials.json').then(response => {
    if (!response.ok) throw new Error('Dataset unavailable');
    return response.json();
  }).then(d => {
    const needed = ['world_population','daily_food_supply_kcal_per_capita','minimum_calorie_need_kcal','global_electricity_generation_twh','modern_energy_minimum_kwh_per_year','renewable_freshwater_km3','minimum_water_need_l_per_day','world_gdp_nominal_usd','extreme_poverty_line_usd_per_day'];
    if (needed.some(key => !Number.isFinite(d[key]?.value) || d[key].value <= 0)) throw new Error('Dataset invalid');
    const food = d.daily_food_supply_kcal_per_capita.value;
    const foodRef = d.minimum_calorie_need_kcal.value;
    const energy = d.global_electricity_generation_twh.value * 1e9 / d.world_population.value;
    const energyRef = d.modern_energy_minimum_kwh_per_year.value;
    const water = d.renewable_freshwater_km3.value * 1e12 / d.world_population.value / 365;
    const waterRef = d.minimum_water_need_l_per_day.value;
    const output = d.world_gdp_nominal_usd.value / d.world_population.value / 365;
    resources = {
      food: {kicker:'Food / Global dietary energy supply',title:'Enough calories. Unequal access.',description:'The global average food supply is above this project’s calorie reference. That does not mean everyone can afford a nutritious diet.',ratio:format(food/foodRef,2),suffix:'×',caption:'global supply / calorie reference',supplyLabel:'Average food supply',supplyValue:format(food)+' kcal',referenceLabel:'Project calorie reference',referenceValue:format(foodRef)+' kcal',referencePercent:foodRef/food*100,unit:'Per person, per day · linear scale',caveat:'Food supply is not intake. Calorie needs vary with age, body size and activity; the 2,100 kcal figure is a project reference, not a universal requirement. Supply already excludes feed and post-harvest losses.',source:d.daily_food_supply_kcal_per_capita,reference:d.minimum_calorie_need_kcal},
      energy: {kicker:'Electricity / Generation',title:'Power exists. Connections matter.',description:'World electricity generation per person exceeds the Modern Energy Minimum used here. Transmission, reliability and local access determine what reaches a home.',ratio:format(energy/energyRef,2),suffix:'×',caption:'global generation / Modern Energy Minimum',supplyLabel:'Electricity generated',supplyValue:format(energy)+' kWh',referenceLabel:'Modern Energy Minimum',referenceValue:format(energyRef)+' kWh',referencePercent:energyRef/energy*100,unit:'Per person, per year · linear scale',caveat:'Generation is not delivered electricity: it includes industrial use and precedes grid losses. The 1,000 kWh benchmark includes household and non-household consumption. An annual average cannot establish reliable local service.',source:d.global_electricity_generation_twh,reference:d.modern_energy_minimum_kwh_per_year},
      water: {kicker:'Water / Renewable freshwater resources',title:'A water cycle. Not a tap.',description:'Dividing renewable freshwater by population shows the scale of the resource. It does not measure safe drinking water available to each person.',ratio:format(water/waterRef),suffix:'×',caption:'renewable resource / domestic water reference',supplyLabel:'Renewable freshwater',supplyValue:format(water)+' L',referenceLabel:'Domestic water reference',referenceValue:format(waterRef)+' L',referencePercent:waterRef/water*100,unit:'Per person, per day · linear scale',caveat:'These are long-term resource flows, not all usable supply. Ecosystems, agriculture and industry also need water. Geography, seasonality, treatment and infrastructure constrain access; this ratio is not an extractable surplus.',source:d.renewable_freshwater_km3,reference:d.minimum_water_need_l_per_day},
      output: {kicker:'Output / Nominal GDP',title:'Economic output isn’t a paycheck.',description:'World GDP divided by population and days in a year. This describes the scale of economic activity, not the money any person receives.',ratio:'$'+format(output,2),suffix:'',caption:'current US dollars per person, per day',supplyLabel:'',supplyValue:'',referenceLabel:'',referenceValue:'',referencePercent:0,unit:'2025 nominal GDP ÷ 8.2 billion people ÷ 365 days',caveat:'GDP is output, not household income or a distributable cash balance. The poverty line is separately defined as 3.00 international dollars per day in 2021 PPP. These are different units, so there is no GDP-to-poverty ratio here.',source:d.world_gdp_nominal_usd,reference:d.extreme_poverty_line_usd_per_day}
    };
    show('food');
    document.querySelector('.resource-tabs').hidden = false;
    tabs.forEach((tab, index) => {
      tab.addEventListener('click', () => show(tab.dataset.resource));
      tab.addEventListener('keydown', event => {
        let next;
        if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
        if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = tabs.length - 1;
        if (next === undefined) return;
        event.preventDefault();
        tabs[next].focus();
        show(tabs[next].dataset.resource);
      });
    });
  }).catch(() => {
    $('data-status').textContent = 'The interactive dataset could not load. The food comparison above is a static snapshot (2023 supply). Follow its source links, or read all comparisons in the full essay below.';
  });
})();
