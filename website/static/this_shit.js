
// this thing lists banks
function setPse() {
    fetch('/payment_methods')
        .then(async function(response) {
            const paymentMethods = Object.values(await response.json()); // change made here
            // const paymentMethods = await response.json(); 
            const pse = paymentMethods.filter((method) => method.id === 'pse')[0];
            const banksList = pse.financial_institutions;
            const banksListElement = document.getElementById('banksList');
            const selectElement = document.createElement('select');
            selectElement.name = 'financialInstitution';
            selectElement.className = "form-control";

            banksList.forEach(bank => {
                const option = document.createElement('option');
                option.value = bank.id;
                option.textContent = bank.description;
                selectElement.appendChild(option);
            });
            
            banksListElement.appendChild(selectElement);

        }).catch(function(reason) {
            console.error('Failed to get payment methods', reason);
        });
}

// the last thing 
(function initCheckout() {
    try {
        const docTypeElement = document.getElementById('form-checkout__identificationType');
        setPse();
        updateSelectOptions('natural')
    }catch(e) {
        return console.error('Error getting identificationTypes: ', e);
    }
 })();


document.getElementById('form-checkout__personType').addEventListener('change', e => {
    const personTypesElement = document.getElementById('form-checkout__personType');
    updateSelectOptions(personTypesElement.value);
});
function updateSelectOptions(selectedValue){
    const naturalDocTypes = [
        new Option('C.C', 'CC'),
        new Option('C.E.', 'CE'),
        new Option('Otro', 'Otro')
    ];
    const juridicaDocTypes = [
        new Option('NIT', 'NIT')
    ];
    const idDocTypes = document.getElementById('form-checkout__identificationType');
    
    if(selectedValue === 'natural') {
        idDocTypes.options.length = 0;
        naturalDocTypes.forEach(item => idDocTypes.options.add(item, undefined));
    } else {
        idDocTypes.options.length = 0;
        juridicaDocTypes.forEach(item => idDocTypes.options.add(item, undefined));
    }
}





