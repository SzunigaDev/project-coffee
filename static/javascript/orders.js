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

function increaseDish(id) {
  const dish = dishes.find(dish => dish.id === id);
  if (dish) {
    dish.quantity++;
  }
  updateOrderList();
}

function decreaseDish(id) {
  const dish = dishes.find(dish => dish.id === id);
  if (dish && dish.quantity > 1) {
    dish.quantity--;
  } else {
    dishes = dishes.filter(dish => dish.id !== id);
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
        <div class="btn-group-vertical ms-3" role="group">
          <button type="button" class="btn btn-success btn-sm rounded-circle my-1" onclick="increaseDish('${dish.id}')">
            <i class="fas fa-plus"></i>
          </button>
          <button type="button" class="btn btn-warning btn-sm rounded-circle my-1" onclick="decreaseDish('${dish.id}')">
            <i class="fas fa-minus"></i>
          </button>
          <button type="button" class="btn btn-danger btn-sm rounded-circle my-1" onclick="removeDish('${dish.id}')">
            <i class="fas fa-trash-alt"></i>
          </button>
        </div>
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
