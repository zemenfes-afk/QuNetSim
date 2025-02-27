from qunetsim.components import Host
from qunetsim.components import Network
from qunetsim.objects import Message
from qunetsim.objects import Qubit
from qunetsim.objects import Logger

Logger.DISABLED = True

AMOUNT_TRANSMIT = 5


def alice(host):
    for _ in range(AMOUNT_TRANSMIT):
        s = 'Hi Eve.'
        print("Alice sends: %s" % s)
        host.send_classical('Eve', s, await_ack=True)

    for _ in range(AMOUNT_TRANSMIT):
        print("Alice sends qubit in the |1> state")
        q = Qubit(host)
        q.X()
        host.send_qubit('Eve', q, await_ack=True)


def bob_sniffing_quantum(sender, receiver, qubit):
    # Bob applies an X operation to all qubits that are routed through him
    qubit.X()


def bob_sniffing_classical(sender, receiver, msg):
    # Bob modifies the message content of all classical messages routed through him
    if isinstance(msg, Message):
        msg.content = "** Bob was here :) ** " + msg.content


def eve(host):
    for i in range(AMOUNT_TRANSMIT):
        alice_message = host.get_classical('Alice', wait=5, seq_num=i)
        print("Eve Received classical: %s." % alice_message.content)

    for i in range(AMOUNT_TRANSMIT):
        q = host.get_data_qubit('Alice', wait=10)
        m = q.measure()
        print("Eve measured: %d." % m)


def main():
    network = Network.get_instance()
    nodes = ["Alice", "Bob", "Eve"]
    network.start(nodes)

    host_alice = Host('Alice')
    host_alice.add_connection('Bob')
    host_alice.start()

    host_bob = Host('Bob')
    host_bob.add_connection('Alice')
    host_bob.add_connection('Eve')
    host_bob.start()

    host_eve = Host('Eve')
    host_eve.add_connection('Bob')
    host_eve.start()

    network.add_host(host_alice)
    network.add_host(host_bob)
    network.add_host(host_eve)

    host_bob.q_relay_sniffing = True
    host_bob.q_relay_sniffing_fn = bob_sniffing_quantum

    host_bob.c_relay_sniffing = True
    host_bob.c_relay_sniffing_fn = bob_sniffing_classical

    t1 = host_alice.run_protocol(alice)
    t2 = host_eve.run_protocol(eve)

    t1.join()
    t2.join()

    network.stop(True)
    exit()


if __name__ == '__main__':
    main()
