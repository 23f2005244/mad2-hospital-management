<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f0f2f5;
}

.sidebar {
  width: 250px;
  min-height: 100vh;
  background: linear-gradient(180deg, #1a3c5e 0%, #2c7be5 100%);
  position: fixed;
  left: 0;
  top: 0;
  padding: 20px 0;
  z-index: 100;
}

.sidebar-brand {
  color: white;
  font-size: 1.3rem;
  font-weight: bold;
  padding: 10px 20px 30px;
  border-bottom: 1px solid rgba(255,255,255,0.2);
  margin-bottom: 10px;
}

.sidebar-nav a {
  display: block;
  color: rgba(255,255,255,0.8);
  padding: 12px 20px;
  text-decoration: none;
  transition: all 0.3s;
  font-size: 0.95rem;
}

.sidebar-nav a:hover,
.sidebar-nav a.router-link-active {
  background: rgba(255,255,255,0.15);
  color: white;
  padding-left: 28px;
}

.sidebar-nav a i {
  margin-right: 10px;
  width: 20px;
}

.main-content {
  margin-left: 250px;
  padding: 30px;
  min-height: 100vh;
}

.card {
  border: none;
  border-radius: 12px;
  box-shadow: 0 2px 15px rgba(0,0,0,0.08);
  margin-bottom: 20px;
}

.card-header {
  background: white;
  border-bottom: 1px solid #eee;
  border-radius: 12px 12px 0 0 !important;
  padding: 15px 20px;
  font-weight: 600;
}

.stat-card {
  border-radius: 12px;
  padding: 20px;
  color: white;
  margin-bottom: 20px;
}

.stat-card h3 {
  font-size: 2rem;
  font-weight: bold;
}

.stat-card p {
  margin: 0;
  opacity: 0.9;
}

.btn-primary {
  background: #2c7be5;
  border-color: #2c7be5;
}

.btn-primary:hover {
  background: #1a68d1;
  border-color: #1a68d1;
}

.table th {
  background: #f8f9fa;
  font-weight: 600;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge {
  font-size: 0.8rem;
  padding: 5px 10px;
}
</style>