document.addEventListener('DOMContentLoaded', function () {
    // Carregar dados do JSON
    fetch('/js/capacity.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao carregar capacity.json');
            }
            return response.json();
        })
        .then(data => {
            const professionalLicenseSelect = document.getElementById('professionalLicense');
            const competenceDiv = document.getElementById('competence');
            const competenceElementsSelect = document.getElementById('competenceElements');
            const capacityDiv = document.getElementById('capacity');
            const capacityLabel = document.getElementById('capacityLabel');
            const capacityOptionsSelect = document.getElementById('capacityOptions');
            const knowledgeDiv = document.getElementById('knowledge');
            const knowledgeListsDiv = document.getElementById('knowledgeLists');

            professionalLicenseSelect.addEventListener('change', function () {
                const selectedValue = this.value;

                // Limpar o conteúdo anterior
                competenceElementsSelect.innerHTML = '';
                capacityOptionsSelect.innerHTML = '';
                capacityLabel.textContent = '';
                knowledgeListsDiv.innerHTML = '';
                competenceDiv.classList.add('hidden');
                capacityDiv.classList.add('hidden');
                knowledgeDiv.classList.add('hidden');

                if (data[selectedValue]) {
                    // Preencher o select de Elementos de Competência
                    for (const [key, value] of Object.entries(data[selectedValue].competenceElements)) {
                        const option = document.createElement('option');
                        option.value = key;
                        option.textContent = value.label;
                        competenceElementsSelect.appendChild(option);
                    }

                    competenceDiv.classList.remove('hidden');
                }
            });

            competenceElementsSelect.addEventListener('change', function () {
                const selectedProfessionalValue = professionalLicenseSelect.value;
                const selectedCompetenceValue = this.value;

                // Limpar o conteúdo anterior
                capacityOptionsSelect.innerHTML = '';
                capacityLabel.textContent = '';
                knowledgeListsDiv.innerHTML = '';
                knowledgeDiv.classList.add('hidden');

                if (data[selectedProfessionalValue] && data[selectedProfessionalValue].competenceElements[selectedCompetenceValue]) {
                    const competenceData = data[selectedProfessionalValue].competenceElements[selectedCompetenceValue];

                    // Criar label
                    capacityLabel.textContent = `Capacidade - ${competenceData.label}`;

                    // Criar select options
                    competenceData.capacities.forEach(capacity => {
                        const opt = document.createElement('option');
                        opt.value = capacity.value;
                        opt.textContent = capacity.text;
                        capacityOptionsSelect.appendChild(opt);
                    });

                    capacityDiv.classList.remove('hidden');
                } else {
                    capacityDiv.classList.add('hidden');
                }
            });

            capacityOptionsSelect.addEventListener('change', function () {
                const selectedProfessionalValue = professionalLicenseSelect.value;
                const selectedCompetenceValue = competenceElementsSelect.value;
                const selectedCapacityValue = this.value;

                // Limpar o conteúdo anterior
                knowledgeListsDiv.innerHTML = '';

                // Obter a lista de conhecimento a partir do JSON carregado
                const competenceData = data[selectedProfessionalValue].competenceElements[selectedCompetenceValue];
                const capacityData = competenceData.capacities.find(capacity => capacity.value === selectedCapacityValue);

                if (capacityData && capacityData.knowledge) {
                    const knowledgeList = data[selectedProfessionalValue].objetos_de_conhecimento;
                    const sublist = document.createElement('ul');
                    capacityData.knowledge.forEach(knowledgeId => {
                        const listItem = document.createElement('li');
                        listItem.textContent = knowledgeList[knowledgeId];
                        sublist.appendChild(listItem);
                    });
                    knowledgeListsDiv.appendChild(sublist);
                    knowledgeDiv.classList.remove('hidden');
                } else {
                    knowledgeDiv.classList.add('hidden');
                }
            });
        })
        .catch(error => console.error('Erro ao carregar dados:', error));
});
