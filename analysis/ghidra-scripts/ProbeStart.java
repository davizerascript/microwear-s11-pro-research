import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;

public class ProbeStart extends GhidraScript {
    @Override
    public void run() throws Exception {
        Address pc = currentProgram.getMinAddress();
        println("program=" + currentProgram.getName());
        println("imageBase=" + currentProgram.getImageBase());
        println("language=" + currentProgram.getLanguage().getLanguageID());
        for (int n = 0; n < 24 && pc != null; n++) {
            disassemble(pc);
            Instruction ins = currentProgram.getListing().getInstructionAt(pc);
            if (ins == null) {
                println("decode-failed-at=" + pc);
                return;
            }
            StringBuilder operands = new StringBuilder();
            for (int i = 0; i < ins.getNumOperands(); i++) {
                if (i > 0) operands.append(", ");
                operands.append(ins.getDefaultOperandRepresentation(i));
            }
            println(String.format("%s: %-12s %s  ; len=%d", ins.getAddress(), ins.getMnemonicString(), operands, ins.getLength()));
            pc = ins.getAddress().add(ins.getLength());
        }
    }
}
