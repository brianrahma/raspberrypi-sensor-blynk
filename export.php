<?php
$servername = "localhost";
$username = "root"; // Ganti dengan username database Anda
$password = ""; // Ganti dengan password database Anda
$dbname = "sensor_data";

// Membuat koneksi
$conn = new mysqli($servername, $username, $password, $dbname);

// Mengecek koneksi
if ($conn->connect_error) {
    die("Koneksi gagal: " . $conn->connect_error);
}

// Menampilkan semua data dari table sensor_readings berdasarkan id secara Descending
$query = "SELECT * FROM sensor_readings ORDER BY id DESC";
$result = $conn->query($query);

// Membuat nama file
$filename = "data_sensor-" . date('Ymd') . ".xls";

// Koding untuk export ke excel
header("Content-type: application/vnd-ms-excel");
header("Content-Disposition: attachment; filename=$filename");

?>
<table class="text-center" border="1">
    <thead class="text-center">
        <tr>
            <th>No.</th>
            <th>ID</th>
            <th>Jarak</th>
            <th>Intensitas Cahaya</th>
            <th>Suhu</th>
            <th>Timestamp</th>
        </tr>
    </thead>
    <tbody class="text-center">
        <?php
        if ($result->num_rows > 0) {
            $no = 1;
            // Menampilkan data
            while ($row = $result->fetch_assoc()) : ?>
        <tr>
            <td><?= $no++; ?></td>
            <td><?= $row['id']; ?></td>
            <td><?= $row['distance']; ?></td>
            <td><?= $row['light']; ?></td>
            <td><?= $row['temp']; ?></td>
            <td><?= $row['timestamp']; ?></td>
        </tr>
        <?php
            endwhile;
        } else {
            echo "<tr><td colspan='6'>Tidak ada data</td></tr>";
        }
        ?>
    </tbody>
</table>

<?php
// Menutup koneksi
$conn->close();
?>
