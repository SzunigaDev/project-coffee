let dishes = [];

function addDish(id, name, price) {
  const quantity = parseInt(document.getElementById(`quantity_${id}`).value);

  const existingDish = dishes.find(dish => dish.id === id);
  if (existingDish) {
    existingDish.quantity += quantity;
  } else {
    const dish = {
      id: id,
      name: name,
      price: parseFloat(price),
      quantity: quantity
    };
    dishes.push(dish);
  }
  updateOrderList();
}

function removeDish(id) {
  dishes = dishes.filter(dish => dish.id !== id);
  updateOrderList();
}

function updateOrderList() {
  const orderList = document.getElementById('order-list');
  orderList.innerHTML = '';
  let total = 0;

  dishes.forEach(dish => {
    const listItem = document.createElement('li');
    listItem.className = 'list-group-item d-flex justify-content-between align-items-start';
    listItem.innerHTML = `
        <div class="ms-2 me-auto">
          <div class="fw-bold">${dish.name}</div>
          Precio Unitario: $${dish.price.toFixed(2)} x ${dish.quantity} = $${(dish.price * dish.quantity).toFixed(2)}
        </div>
        <span class="badge text-bg-primary rounded-pill">${dish.quantity}</span>
        <button type="button" class="btn btn-danger btn-sm ms-3 rounded-circle" onclick="removeDish('${dish.id}')">
          <i class="fas fa-trash-alt"></i>
        </button>
      `;
    orderList.appendChild(listItem);
    total += dish.price * dish.quantity;
  });

  const totalItem = document.createElement('li');
  totalItem.className = 'list-group-item active';
  totalItem.textContent = `Total: $${total.toFixed(2)}`;
  orderList.appendChild(totalItem);
}

function placeOrder() {
  const tableNumber = document.getElementById('table_number').value;
  if (dishes.length > 0) {
    fetch(createOrderUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        table_number: tableNumber,
        dishes: dishes
      })
    }).then(response => {
      if (response.ok) {
        alertify.success('Pedido realizado con éxito');
        dishes = [];
        updateOrderList();
      } else {
        alertify.error('Hubo un problema al realizar el pedido');
      }
    });
  } else {
    alertify.error('Oops! La órden está vacía 😅');
  }
}
