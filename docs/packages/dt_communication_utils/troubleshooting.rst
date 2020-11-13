Troubleshooting
---------------

I don't receive messages
^^^^^^^^^^^^^^^^^^^^^^^^

For UDP Multicast (UDPm) to work properly, the kernel of your Operating System has to have a route
for UDPm traffic. This means that a network interface has to be identified as the gateway for
such traffic. When no explicit route exists, the default gateway is selected.

This can result in missing messages on computers where multiple network interfaces exist.
For example, if you have a computer with two interfaces, say ``eth0`` connected to a WAN and
``eth1`` connected to a LAN, your default gateway will (most likely) be ``eth0``,
because it is the one with access to the internet.

If you create a Communication Group on such computer, the UDPm traffic will enter/leave
your computer through the interface ``eth0``. This means that any message incoming from a
device within your LAN will not be received, and similarly, no messages leaving your computer
will ever reach any device on your LAN.

This can be fixed by explicitly telling your kernel which interface should be responsible
for UDPm traffic. You can do so by running the command,

..  code-block:: bash

    sudo route add -net 224.0.0.0 netmask 240.0.0.0 dev DEVICE

where you replace ``DEVICE`` with the network interface your LAN is connected to (e.g., ``eth1``
in the example above).