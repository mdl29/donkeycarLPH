cube(size=[100, 100, 3]);
difference() {
    translate([50, 50, 3]) cylinder(h=70, r=40, $fn=100);
translate([50, 100, 73]) rotate([90, 0, 0]) {
    cylinder(h=100, r=30, $fn=100);
}
}
