import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class MarkEntry extends GhidraScript {
    @Override
    public void run() throws Exception {
        Address start = currentProgram.getMinAddress();
        if (currentProgram.getListing().getInstructionAt(start) == null && !disassemble(start)) {
            println("entry probe failed at " + start);
            return;
        }
        Function existing = currentProgram.getFunctionManager().getFunctionAt(start);
        if (existing == null) {
            Function f = createFunction(start, "entry_provisional_offset_0");
            println("created provisional function=" + (f != null));
        } else {
            println("existing function at provisional offset 0=" + existing.getName());
        }
    }
}
