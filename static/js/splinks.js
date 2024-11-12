fetch('/js/splinks.json')
    .then(response => response.json())
    .then(data => displayCategories(data))
    .catch(error => console.error('Erro ao carregar os dados:', error));

function displayCategories(data) {
    const container = document.getElementById('categorias-container');

    const groupedData = data.reduce((acc, item) => {
        if (!acc[item.categoria]) {
            acc[item.categoria] = [];
        }
        acc[item.categoria].push(item);
        return acc;
    }, {});

    for (const [categoria, items] of Object.entries(groupedData)) {
        const categoriaDiv = document.createElement('div');
        categoriaDiv.classList.add('categoria');
        
        const labelContainer = document.createElement('div');
        labelContainer.classList.add('label-container');
        
        const label = document.createElement('label');
        label.textContent = categoria;
        labelContainer.appendChild(label);
        categoriaDiv.appendChild(labelContainer);

        const itemsContainer = document.createElement('div');
        itemsContainer.classList.add('items-container');  // Adiciona a div para conter os itens
        
        items.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.classList.add('item');
            
            const img = document.createElement('img');
            img.src = item.img;
            img.alt = item.nome;

            const linkDescricaoDiv = document.createElement('div');
            linkDescricaoDiv.classList.add('link-descricao');  // Adiciona uma nova div para link e descricao

            const link = document.createElement('a');
            link.href = item.link;
            link.textContent = item.nome;
            link.target = '_blank';
            // O novo site não saberá de onde veio o usuario
            // link.rel= 'noreferrer'

            const descricao = document.createElement('label');
            descricao.textContent = item.descricao;

            linkDescricaoDiv.appendChild(link);
            linkDescricaoDiv.appendChild(descricao);

            itemDiv.appendChild(img);
            itemDiv.appendChild(linkDescricaoDiv);
            itemsContainer.appendChild(itemDiv);  // Adiciona o item à nova div
        });

        categoriaDiv.appendChild(itemsContainer);  // Adiciona a nova div à categoria
        container.appendChild(categoriaDiv);
    }
}
