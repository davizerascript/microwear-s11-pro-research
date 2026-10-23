import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import java.util.HashSet;
import java.util.Set;

public class DriverRefs extends GhidraScript {
    private void inspect(String label, long offset, int length) throws Exception {
        println("--- " + label + " @ " + Long.toHexString(offset) + " ---");
        Set<String> seen = new HashSet<>();
        for (int i = 0; i < length; i++) {
            Address target = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(offset + i);
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(target);
            while (refs.hasNext()) {
                Reference ref = refs.next();
                String key = ref.getFromAddress().toString() + "/" + ref.getReferenceType();
                if (!seen.add(key)) continue;
                Function f = currentProgram.getFunctionManager().getFunctionContaining(ref.getFromAddress());
                Instruction ins = currentProgram.getListing().getInstructionContaining(ref.getFromAddress());
                println("xref from=" + ref.getFromAddress() + " type=" + ref.getReferenceType() +
                        " function=" + (f == null ? "(none)" : f.getName()) +
                        " instruction=" + (ins == null ? "(data)" : ins.toString()));
            }
        }
        println("xref_count=" + seen.size());
    }

    @Override
    public void run() throws Exception {
        println("program=" + currentProgram.getName() + " language=" + currentProgram.getLanguage().getLanguageID() +
                " base=" + currentProgram.getImageBase());
        inspect("sh8601", 0xcd618L, 6);
        inspect("gc9b71", 0xcd61fL, 6);
        inspect("bcs_touch", 0x168bf6L, 9);
    }
}
